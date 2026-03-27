"""Billing API routes."""
from __future__ import annotations
from datetime import date, timedelta
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.prodamus import create_payment_link
from app.core.security import get_current_user
from app.models import (
    Balance, CreditLedger, PaymentMethod, PaymentOrder,
    PublicModelTariff, RechargePackage, UserLoyalty, UserPortalProfile,
    UsageBillingSnapshot
)
from app.schemas import (
    BalanceOut, CreateOrderRequest, CreateOrderResponse,
    LoyaltyOut, OrderOut, OrdersResponse, PackageOut,
    PackagesResponse, PaymentMethodOut
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["billing"])


def _get_bonus_tier(amount_rub: int) -> float:
    if amount_rub >= 25500:
        return 10.0
    if amount_rub >= 17000:
        return 7.0
    if amount_rub >= 10200:
        return 5.0
    if amount_rub >= 5100:
        return 3.0
    return 0.0


async def _get_user(db: AsyncSession, token_data) -> UserPortalProfile:
    result = await db.execute(
        select(UserPortalProfile).where(UserPortalProfile.email == token_data.username)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/balance", response_model=BalanceOut)
async def get_balance(current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    user = await _get_user(db, current_user)
    bal = await db.get(Balance, user.id)
    loyalty = await db.get(UserLoyalty, user.id)
    rub = float(bal.balance_credits * bal.fixed_rub_per_credit) if bal else 0
    remaining = max(0, settings.LOYALTY_THRESHOLD_RUB - (loyalty.lifetime_paid_rub if loyalty else 0))
    progress = min(100, ((loyalty.lifetime_paid_rub if loyalty else 0) / settings.LOYALTY_THRESHOLD_RUB) * 100)
    return BalanceOut(
        balance_credits=float(bal.balance_credits) if bal else 0,
        balance_rub=rub,
        rub_per_credit=float(settings.FIXED_RUB_PER_CREDIT),
        loyalty=LoyaltyOut(
            tier=loyalty.loyalty_tier if loyalty else "none",
            discount_percent=float(loyalty.usage_discount_percent) if loyalty else 0,
            lifetime_paid_rub=loyalty.lifetime_paid_rub if loyalty else 0,
            remaining_to_silver=remaining,
            progress_percent=round(progress, 1)
        )
    )


@router.get("/packages", response_model=PackagesResponse)
async def get_packages(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(RechargePackage).where(RechargePackage.is_active == True).order_by(RechargePackage.sort_order)
    )
    pkgs = result.scalars().all()
    return PackagesResponse(
        packages=[PackageOut.model_validate(p) for p in pkgs],
        custom_topup={"min_rub": 300, "step_rub": 50,
                      "bonus_tiers": [
                          {"min_rub": 0, "max_rub": 5099, "bonus_percent": 0},
                          {"min_rub": 5100, "max_rub": 10199, "bonus_percent": 3},
                          {"min_rub": 10200, "max_rub": 16999, "bonus_percent": 5},
                          {"min_rub": 17000, "max_rub": 25499, "bonus_percent": 7},
                          {"min_rub": 25500, "max_rub": None, "bonus_percent": 10},
                      ]}
    )


@router.get("/payment-methods")
async def get_payment_methods(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(PaymentMethod).where(PaymentMethod.is_active == True)
    )
    methods = result.scalars().all()
    return {"methods": [PaymentMethodOut.model_validate(m) for m in methods]}


@router.get("/loyalty", response_model=LoyaltyOut)
async def get_loyalty(current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    user = await _get_user(db, current_user)
    loyalty = await db.get(UserLoyalty, user.id)
    remaining = max(0, settings.LOYALTY_THRESHOLD_RUB - (loyalty.lifetime_paid_rub if loyalty else 0))
    progress = min(100, ((loyalty.lifetime_paid_rub if loyalty else 0) / settings.LOYALTY_THRESHOLD_RUB) * 100)
    return LoyaltyOut(
        tier=loyalty.loyalty_tier if loyalty else "none",
        discount_percent=float(loyalty.usage_discount_percent) if loyalty else 0,
        lifetime_paid_rub=loyalty.lifetime_paid_rub if loyalty else 0,
        remaining_to_silver=remaining,
        progress_percent=round(progress, 1)
    )


@router.post("/create-order", response_model=CreateOrderResponse)
async def create_order(req: CreateOrderRequest, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    user = await _get_user(db, current_user)

    if req.package_code:
        result = await db.execute(
            select(RechargePackage).where(RechargePackage.code == req.package_code, RechargePackage.is_active == True)
        )
        pkg = result.scalar_one_or_none()
        if not pkg:
            raise HTTPException(status_code=404, detail="Package not found")
        pay_rub = pkg.pay_rub
        credited_credits = pkg.credited_credits
        bonus = pkg.bonus_percent
        pkg_id = pkg.id
    elif req.custom_amount_rub:
        amt = req.custom_amount_rub
        if amt < 300:
            raise HTTPException(status_code=400, detail="Minimum top-up is 300 ₽")
        if amt % 50 != 0:
            raise HTTPException(status_code=400, detail="Amount must be in 50 ₽ steps")
        pay_rub = amt
        bonus = Decimal(str(_get_bonus_tier(amt)))
        credited_credits = Decimal(str(amt / settings.FIXED_RUB_PER_CREDIT)) * (1 + bonus / 100)
        pkg_id = None
    else:
        raise HTTPException(status_code=400, detail="Provide package_code or custom_amount_rub")

    pm_result = await db.execute(
        select(PaymentMethod).where(PaymentMethod.code == (req.payment_method_code or "prodamus_card"))
    )
    pm = pm_result.scalar_one_or_none()

    order = PaymentOrder(
        id=uuid4(), user_id=user.id, package_id=pkg_id,
        custom_amount_rub=req.custom_amount_rub, amount_paid_rub=int(pay_rub),
        credited_credits=credited_credits, bonus_percent=bonus,
        payment_method_id=pm.id if pm else None, status="pending"
    )
    db.add(order)
    await db.commit()

    # mode="pay" строит прямой URL с параметрами — подтверждён working (do=link confirmed live)
    payment_url = create_payment_link(
        mode="pay", amount_rub=int(pay_rub),
        product_name="ProAICommunity Top-up",
        order_id=str(order.id), secret_key=settings.PRODAMUS_SECRET_KEY,
        base_url=settings.PRODAMUS_BASE_URL
    )
    return CreateOrderResponse(
        order_id=str(order.id), amount_rub=int(pay_rub),
        credited_credits=float(credited_credits), bonus_percent=float(bonus),
        payment_url=payment_url, status="pending"
    )


@router.get("/orders", response_model=OrdersResponse)
async def get_orders(
    current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1), per_page: int = Query(20, ge=1, le=100)
):
    user = await _get_user(db, current_user)
    total_r = await db.execute(
        select(func.count(PaymentOrder.id)).where(PaymentOrder.user_id == user.id)
    )
    total = total_r.scalar() or 0
    offset = (page - 1) * per_page
    result = await db.execute(
        select(PaymentOrder).where(PaymentOrder.user_id == user.id)
        .order_by(PaymentOrder.created_at.desc()).offset(offset).limit(per_page)
    )
    orders = result.scalars().all()
    return OrdersResponse(
        orders=[OrderOut(
            id=str(o.id), package_name="Custom" if o.custom_amount_rub else "Package",
            amount_paid_rub=o.amount_paid_rub, credited_credits=float(o.credited_credits),
            bonus_percent=float(o.bonus_percent), payment_method="Card",
            status=o.status, created_at=o.created_at.isoformat(),
            paid_at=o.paid_at.isoformat() if o.paid_at else None
        ) for o in orders], total=total, page=page, per_page=per_page
    )


@router.get("/order/{order_id}")
async def get_order(order_id: UUID, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    user = await _get_user(db, current_user)
    order = await db.get(PaymentOrder, order_id)
    if not order or order.user_id != user.id:
        raise HTTPException(status_code=404, detail="Order not found")
    return OrderOut(
        id=str(order.id), package_name="Custom" if order.custom_amount_rub else "Package",
        amount_paid_rub=order.amount_paid_rub, credited_credits=float(order.credited_credits),
        bonus_percent=float(order.bonus_percent), payment_method="Card",
        status=order.status, created_at=order.created_at.isoformat(),
        paid_at=order.paid_at.isoformat() if order.paid_at else None
    )

# ---------------------------------------------------------------------------
# BLOCK A: GET /models/tariffs — публичный каталог тарифов
# ---------------------------------------------------------------------------
@router.get("/models/tariffs")
async def get_model_tariffs(db: AsyncSession = Depends(get_db)):
    """Возвращает все активные тарифы для отображения в кабинете."""
    result = await db.execute(
        select(PublicModelTariff)
        .where(PublicModelTariff.is_active == True)
        .order_by(PublicModelTariff.public_model_name)
    )
    tariffs = result.scalars().all()
    return {"tariffs": [
        {
            "model": t.public_model_name,
            "billing_unit": t.billing_unit,
            "input_rate_credits": float(t.input_rate_credits),
            "output_rate_credits": float(t.output_rate_credits),
            "input_rub_per_1k": round(float(t.input_rate_credits) * 85 * 1000, 4),
            "output_rub_per_1k": round(float(t.output_rate_credits) * 85 * 1000, 4),
            "notes": t.notes,
        }
        for t in tariffs
    ]}


# ---------------------------------------------------------------------------
# BLOCK C: GET /usage-logs — детальные логи списаний с фильтрами
# ---------------------------------------------------------------------------
@router.get("/usage-logs")
async def get_usage_logs(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    date_from: Optional[str] = Query(None, description="YYYY-MM-DD"),
    date_to: Optional[str] = Query(None, description="YYYY-MM-DD"),
    model: Optional[str] = Query(None),
    key: Optional[str] = Query(None, description="api_key_hash prefix"),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
):
    """Детальная таблица usage-записей с фильтрами для кабинета."""
    user = await _get_user(db, current_user)

    from sqlalchemy import and_
    conditions = [UsageBillingSnapshot.user_id == user.id]

    if date_from:
        try:
            dt_from = date.fromisoformat(date_from)
            conditions.append(UsageBillingSnapshot.created_at >= dt_from.isoformat())
        except ValueError:
            pass
    if date_to:
        try:
            dt_to = date.fromisoformat(date_to)
            from datetime import timedelta
            conditions.append(UsageBillingSnapshot.created_at < (dt_to + timedelta(days=1)).isoformat())
        except ValueError:
            pass
    if model:
        conditions.append(UsageBillingSnapshot.public_model_name == model)
    if key:
        conditions.append(UsageBillingSnapshot.api_key_hash.like(f"{key}%"))

    total_r = await db.execute(
        select(func.count(UsageBillingSnapshot.id)).where(and_(*conditions))
    )
    total = total_r.scalar() or 0

    offset = (page - 1) * per_page
    result = await db.execute(
        select(UsageBillingSnapshot)
        .where(and_(*conditions))
        .order_by(UsageBillingSnapshot.created_at.desc())
        .offset(offset).limit(per_page)
    )
    rows = result.scalars().all()

    # P0 transparency: batch lookup billing_unit из public_model_tariff
    from sqlalchemy import text as _sa_text
    _model_names = list({r.public_model_name for r in rows if r.public_model_name})
    _bu_map = {}
    if _model_names:
        _phs = ", ".join(f":_m{i}" for i in range(len(_model_names)))
        _params = {f"_m{i}": name for i, name in enumerate(_model_names)}
        _tu = await db.execute(
            _sa_text(f"SELECT public_model_name, billing_unit FROM billing.public_model_tariff WHERE public_model_name IN ({_phs})"),
            _params
        )
        _bu_map = {row[0]: row[1] for row in _tu.fetchall()}

    _PROXY_UNITS = {"audio_token", "search_token", "realtime_token", "research_token"}
    _CAVEAT_MAP = {
        "audio_token": "Audio processing costs are based on transcript token volume. Best-effort approximation.",
        "search_token": "Search requests include a per-query overhead. Best-effort approximation.",
        "realtime_token": "Realtime session costs include streaming overhead. Best-effort approximation.",
        "research_token": "Deep research tasks run multiple internal steps. Best-effort approximation.",
    }

    def _billing_label(model_name, bu_map):
        return "Estimated" if bu_map.get(model_name) in _PROXY_UNITS else "Standard"

    def _caveat_text(model_name, bu_map):
        unit = bu_map.get(model_name)
        return _CAVEAT_MAP.get(unit) if unit in _PROXY_UNITS else None

    return {
        "logs": [
            {
                "id": str(r.id),
                "created_at": r.created_at.isoformat(),
                "model": r.public_model_name or "",
                "api_key_prefix": (r.api_key_hash or "")[:12] + "...",
                "input_tokens": r.input_tokens,
                "output_tokens": r.output_tokens,
                "charged_credits": float(r.charged_credits),
                "loyalty_discount_percent": float(r.loyalty_discount_percent),
                "billing_type_label": _billing_label(r.public_model_name, _bu_map),
                "proxy_billed": _billing_label(r.public_model_name, _bu_map) == "Estimated",
                "caveat_text": _caveat_text(r.public_model_name, _bu_map),
            }
            for r in rows
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page if total > 0 else 1,
    }
