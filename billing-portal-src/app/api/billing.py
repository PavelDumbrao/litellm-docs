"""Billing API routes."""
from __future__ import annotations
from datetime import date, timedelta
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
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

OPERATOR_ECONOMICS_SNAPSHOT_DATE = "2026-03-27"
OPERATOR_ECONOMICS_MODEL_MATRIX_TSV = """gpt-4o-audio-preview	Audio/Speech	audio_token	Estimated	https://poloai.top/v1	1	1.029444	4.108333	0.514	2.055	50.07	49.98	2
gpt-audio	Audio/Speech	audio_token	Estimated	https://poloai.top/v1		1.029444	2.049444	0.514	1.027	50.07	49.89	1
gpt-audio-mini	Audio/Speech	audio_token	Estimated	https://poloai.top/v1		30.826667	61.653333	15.411	30.822	50.01	50.01	1
claude-haiku-4-5	Claude	token	Exact	https://anideaai.com/v1	1	1.596111	7.999444	0.056	0.28	96.49	96.5	2
claude-haiku-4-5-thinking	Claude	token	Exact	https://poloai.top/v1		1.596111	7.999444	0.11	0.548	93.11	93.15	2
claude-opus-4-5-thinking	Claude	token	Exact	https://poloai.top/v1		29.995556	149.996667	0.548	2.74	98.17	98.17	2
claude-opus-4-6	Claude	token	Exact	https://anideaai.com/v1	1	29.995556	149.996667	0.28	1.4	99.07	99.07	2
claude-opus-4-6-thinking	Claude	token	Exact	https://jeniya.top/v1		29.995556	149.996667	0.822	4.11	97.26	97.26	1
claude-sonnet-4-5-thinking	Claude	token	Exact	https://poloai.top/v1		5.997222	29.995556	0.329	1.644	94.51	94.52	2
claude-sonnet-4-6	Claude	token	Exact	https://anideaai.com/v1	1	5.997222	29.995556	0.17	0.84	97.17	97.2	2
text-embedding-3-large	Embeddings	token	Exact	https://poloai.top/v1	1	0.264444	0.0	0.027	0.027	89.79		2
text-embedding-3-small	Embeddings	token	Exact	https://poloai.top/v1	1	0.037778	0.0	0.004	0.004	89.41		2
text-embedding-ada-002	Embeddings	token	Exact	https://poloai.top/v1	1	0.198333	0.0	0.021	0.021	89.41		2
gemini-2.5-flash	Gemini	token	Exact	https://jeniya.top/v1	1	0.302222	1.199444	0.032	0.268	89.41	77.66	2
gemini-2.5-flash-lite	Gemini	token	Exact	https://poloai.top/v1		0.198333	0.802778	0.014	0.055	92.94	93.15	1
gemini-2.5-flash-thinking	Gemini	token	Exact	https://poloai.top/v1		0.302222	1.199444	0.041	0.342	86.43	71.49	1
gemini-3-flash-preview	Gemini	token	Exact	https://jeniya.top/v1	1	0.132222	0.821667	0.053	0.321	59.92	60.93	2
gemini-3-flash-preview-nothinking	Gemini	token	Exact	https://poloai.top/v1		0.132222	0.821667	0.068	0.411	48.57	49.98	2
gemini-3-flash-preview-thinking	Gemini	token	Exact	https://poloai.top/v1		0.132222	0.821667	0.068	0.411	48.57	49.98	2
gemini-3.1-pro-preview	Gemini	token	Exact	https://poloai.top/v1		0.547778	3.286667	0.274	1.644	49.98	49.98	1
gemini-3.1-pro-preview-high	Gemini	token	Exact	https://poloai.top/v1		0.547778	3.286667	0.274	1.644	49.98	49.98	2
gemini-3.1-pro-preview-low	Gemini	token	Exact	https://poloai.top/v1		0.547778	3.286667	0.274	1.644	49.98	49.98	2
gemini-3.1-pro-preview-medium	Gemini	token	Exact	https://poloai.top/v1		0.547778	3.286667	0.274	1.644	49.98	49.98	2
gpt-4.1	General Chat	token	Incomplete			4.004444	15.998889					0
gpt-4.1-mini	General Chat	token	Exact	https://poloai.top/v1	1	0.802778	3.192222	0.082	0.329	89.79	89.69	2
gpt-4.1-nano	General Chat	token	Exact	https://poloai.top/v1	1	0.198333	0.802778	0.021	0.082	89.41	89.79	2
gpt-4o	General Chat	token	Exact	https://poloai.top/v1	1	4.996111	20.003333	0.514	2.055	89.71	89.73	2
gpt-4o-mini	General Chat	token	Exact	https://poloai.top/v1	1	0.302222	1.199444	0.031	0.123	89.74	89.75	2
gpt-5.3-codex	General Chat	token	Exact	https://jeniya.top/v1	1	0.377778	2.993889	0.187	1.497	50.5	50.0	2
gpt-5.4	General Chat	token	Exact	https://jeniya.top/v1	1	1.029444	8.216667	0.267	1.604	74.06	80.48	4
gpt-5.4-mini	General Chat	token	Exact	https://jeniya.top/v1	1	0.122778	0.717778	0.06	0.36	51.13	49.85	2
gpt-5.4-nano	General Chat	token	Exact	https://jeniya.top/v1	1	0.037778	0.396667	0.02	0.2	47.06	49.58	2
i7dc-claude-haiku-4-5	I7DC Relay		Incomplete	https://i7dc.com/api				0.15	0.75			1
i7dc-claude-opus-4-6	I7DC Relay		Incomplete	https://i7dc.com/api				0.75	3.75			1
i7dc-claude-sonnet-4-6	I7DC Relay		Incomplete	https://i7dc.com/api				0.45	2.25			1
deepseek-v3.2	Other	token	Exact	https://jeniya.top/v1	1	0.538333	2.200556	0.16	0.241	70.28	89.05	2
gpt-4o-mini-realtime-preview	Realtime	realtime_token	Estimated	https://poloai.top/v1		0.245556	0.982222	0.123	0.493	49.91	49.81	1
gpt-4o-realtime-preview	Realtime	realtime_token	Estimated	https://poloai.top/v1		2.049444	8.216667	1.027	4.11	49.89	49.98	1
gpt-4o-mini-search-preview	Search/Research	search_token	Estimated	https://poloai.top/v1		0.056667	0.226667	0.029	0.115	48.82	49.26	1
gpt-4o-search-preview	Search/Research	search_token	Estimated	https://poloai.top/v1		1.029444	4.108333	0.514	2.055	50.07	49.98	1
gpt-5-search-api	Search/Research	search_token	Estimated	https://poloai.top/v1		1.029444	8.216667	0.514	4.11	50.07	49.98	1
o4-mini-deep-research	Search/Research	research_token	Estimated	https://poloai.top/v1		0.821667	3.286667	0.411	1.644	49.98	49.98	1
gpt-4o-mini-transcribe	Transcription	audio_token	Estimated	https://poloai.top/v1		0.51	2.049444	0.257	1.027	49.61	49.89	1
gpt-4o-transcribe	Transcription	audio_token	Estimated	https://poloai.top/v1	1	1.029444	4.108333	0.514	2.055	50.07	49.98	2"""


def _require_operator_secret(
    x_operator_secret: Optional[str] = Header(None, alias="X-Operator-Secret"),
) -> None:
    """Пускает только внутреннего оператора с секретом из runtime env."""
    import os
    expected_secret = os.environ.get("OPERATOR_SECRET") or getattr(settings, "OPERATOR_SECRET", None)
    if not expected_secret or not x_operator_secret or x_operator_secret != expected_secret:
        raise HTTPException(status_code=403, detail="Forbidden")


def _parse_optional_float(raw: str) -> Optional[float]:
    """Преобразует строку в float или возвращает None для пустого значения."""
    if not raw:
        return None
    return float(raw)


def _parse_optional_int(raw: str) -> Optional[int]:
    """Преобразует строку в int или возвращает None для пустого значения."""
    if not raw:
        return None
    return int(raw)


def _provider_label(api_base: Optional[str]) -> Optional[str]:
    """Возвращает короткую метку провайдера для internal operator view."""
    provider_map = {
        "https://anideaai.com/v1": "ANIDEAAI",
        "https://poloai.top/v1": "POLO",
        "https://jeniya.top/v1": "JENIYA",
        "https://i7dc.com/api": "I7DC",
    }
    return provider_map.get(api_base or "", api_base)


def _build_proxy_caveat(confidence: str, billing_unit: Optional[str]) -> Optional[str]:
    """Возвращает caveat для operator economics rows."""
    if confidence == "Estimated":
        return f"{billing_unit or 'special_unit'}-billing использует proxy economics view и не должен трактоваться как exact."
    if confidence == "Incomplete":
        return "Покрытие economics incomplete: отсутствует retail или provider side truth."
    return None


def _load_operator_economics_model_rows() -> list[dict[str, Any]]:
    """Возвращает модельный economics snapshot, собранный по live-данным на дату аудита."""
    rows: list[dict[str, Any]] = []
    for raw in OPERATOR_ECONOMICS_MODEL_MATRIX_TSV.splitlines():
        line = raw.strip()
        if not line:
            continue
        parts = line.split("\t")
        (
            model,
            category,
            billing_unit,
            confidence,
            api_base,
            order,
            retail_input,
            retail_output,
            cost_input,
            cost_output,
            margin_input,
            margin_output,
            provider_paths_count,
        ) = parts
        rows.append(
            {
                "model": model,
                "category": category,
                "billing_unit": billing_unit or None,
                "confidence": confidence,
                "provider_label": _provider_label(api_base or None),
                "provider_api_base": api_base or None,
                "primary_provider_order": _parse_optional_int(order),
                "provider_paths_count": int(provider_paths_count),
                "retail_input_usd_per_1m": _parse_optional_float(retail_input),
                "retail_output_usd_per_1m": _parse_optional_float(retail_output),
                "provider_input_cost_usd_per_1m": _parse_optional_float(cost_input),
                "provider_output_cost_usd_per_1m": _parse_optional_float(cost_output),
                "input_margin_pct": _parse_optional_float(margin_input),
                "output_margin_pct": _parse_optional_float(margin_output),
                "proxy_caveat": _build_proxy_caveat(confidence, billing_unit or None),
            }
        )
    return rows


def _build_operator_economics_category_rows(
    model_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Строит category-level economics rollup по модельному snapshot."""
    buckets: dict[str, dict[str, Any]] = {}
    for row in model_rows:
        category = row["category"]
        bucket = buckets.setdefault(
            category,
            {
                "category": category,
                "total_models": 0,
                "exact_count": 0,
                "estimated_count": 0,
                "incomplete_count": 0,
                "input_margin_sum": 0.0,
                "input_margin_count": 0,
                "output_margin_sum": 0.0,
                "output_margin_count": 0,
            },
        )
        bucket["total_models"] += 1
        bucket[f"{row['confidence'].lower()}_count"] += 1
        if row["input_margin_pct"] is not None:
            bucket["input_margin_sum"] += row["input_margin_pct"]
            bucket["input_margin_count"] += 1
        if row["output_margin_pct"] is not None:
            bucket["output_margin_sum"] += row["output_margin_pct"]
            bucket["output_margin_count"] += 1

    category_rows: list[dict[str, Any]] = []
    for category in sorted(buckets):
        bucket = buckets[category]
        avg_input = None
        if bucket["input_margin_count"] > 0:
            avg_input = round(bucket["input_margin_sum"] / bucket["input_margin_count"], 2)
        avg_output = None
        if bucket["output_margin_count"] > 0:
            avg_output = round(bucket["output_margin_sum"] / bucket["output_margin_count"], 2)

        note = "Mixed confidence category."
        if bucket["estimated_count"] == bucket["total_models"]:
            note = "Proxy economics only."
        elif bucket["incomplete_count"] == bucket["total_models"]:
            note = "Coverage incomplete."
        elif bucket["exact_count"] == bucket["total_models"]:
            note = "Token-based exact view."

        category_rows.append(
            {
                "category": category,
                "total_models": bucket["total_models"],
                "exact_count": bucket["exact_count"],
                "estimated_count": bucket["estimated_count"],
                "incomplete_count": bucket["incomplete_count"],
                "avg_input_margin_pct": avg_input,
                "avg_output_margin_pct": avg_output,
                "note": note,
            }
        )
    return category_rows


def _build_operator_economics_summary(model_rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Строит верхнеуровневое summary по confidence статусам."""
    exact_count = sum(1 for row in model_rows if row["confidence"] == "Exact")
    estimated_count = sum(1 for row in model_rows if row["confidence"] == "Estimated")
    incomplete_count = sum(1 for row in model_rows if row["confidence"] == "Incomplete")
    return {
        "total_models": len(model_rows),
        "exact_count": exact_count,
        "estimated_count": estimated_count,
        "incomplete_count": incomplete_count,
    }


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


# Модели в стадии тестирования — не в production public surface
# Не участвуют в customer billing, исключены из HIGH-priority remediation
TEST_ONLY_MODELS: frozenset[str] = frozenset({
    "i7dc-claude-haiku-4-5",
    "i7dc-claude-opus-4-6",
    "i7dc-claude-sonnet-4-6",
})


def _evaluate_margin_alerts(model_rows: list[dict]) -> list[dict]:
    """Оценивает каждую модель по threshold matrix и возвращает список alerts."""
    alerts: list[dict] = []

    # Собираем категории для ESTIMATED_ONLY_CATEGORY
    category_confidence: dict[str, set] = {}
    for row in model_rows:
        cat = row["category"]
        category_confidence.setdefault(cat, set()).add(row["confidence"])

    estimated_only_categories = {
        cat for cat, confs in category_confidence.items()
        if confs == {"Estimated"}
    }

    already_alerted_categories: set[str] = set()

    for row in model_rows:
        model = row["model"]
        category = row["category"]
        confidence = row["confidence"]
        in_margin = row["input_margin_pct"]
        out_margin = row["output_margin_pct"]
        in_cost = row["provider_input_cost_usd_per_1m"]
        out_cost = row["provider_output_cost_usd_per_1m"]

        # INCOMPLETE_ECONOMICS (с разделением: test-only vs production)
        if confidence == "Incomplete":
            if model in TEST_ONLY_MODELS:
                alerts.append({
                    "alert_class": "TEST_ONLY_INCOMPLETE",
                    "severity": "LOW",
                    "model": model,
                    "category": category,
                    "confidence": confidence,
                    "scope": "test-only",
                    "input_margin_pct": in_margin,
                    "output_margin_pct": out_margin,
                    "recommended_action": (
                        "Модель в стадии тестирования — не в production public surface. "
                        "Remediation не требуется до перехода в production. "
                        "При production launch: запросить i7dc invoice + создать retail tariff entry."
                    ),
                })
            else:
                alerts.append({
                    "alert_class": "INCOMPLETE_ECONOMICS",
                    "severity": "HIGH",
                    "model": model,
                    "category": category,
                    "confidence": confidence,
                    "scope": "production",
                    "input_margin_pct": in_margin,
                    "output_margin_pct": out_margin,
                    "recommended_action": (
                        "Запросить provider cost данные. "
                        "Если недоступны — рассмотреть деактивацию или explicit markup политику."
                    ),
                })
            continue  # Incomplete — дальше не оцениваем margin

        # NEGATIVE_MARGIN
        if (in_margin is not None and in_margin < 0) or (out_margin is not None and out_margin < 0):
            alerts.append({
                "alert_class": "NEGATIVE_MARGIN",
                "severity": "CRITICAL",
                "model": model,
                "category": category,
                "confidence": confidence,
                "input_margin_pct": in_margin,
                "output_margin_pct": out_margin,
                "recommended_action": (
                    "Немедленно проверить retail tariff vs provider cost. "
                    "Скорректировать retail rate или деактивировать модель."
                ),
            })
            continue

        # LOW_MARGIN_CRITICAL (только для Exact — у Estimated слишком высокая погрешность)
        if confidence == "Exact":
            critical = (
                (in_margin is not None and 0 <= in_margin < 30) or
                (out_margin is not None and 0 <= out_margin < 30)
            )
            if critical:
                alerts.append({
                    "alert_class": "LOW_MARGIN_CRITICAL",
                    "severity": "HIGH",
                    "model": model,
                    "category": category,
                    "confidence": confidence,
                    "input_margin_pct": in_margin,
                    "output_margin_pct": out_margin,
                    "recommended_action": (
                        "Оценить реальный token mix по usage-logs. "
                        "Рассмотреть увеличение retail rate."
                    ),
                })
                continue

        # LOW_MARGIN_WARNING
        warning = (
            (in_margin is not None and 30 <= in_margin < 50) or
            (out_margin is not None and 30 <= out_margin < 50)
        )
        if warning:
            alerts.append({
                "alert_class": "LOW_MARGIN_WARNING",
                "severity": "MEDIUM",
                "model": model,
                "category": category,
                "confidence": confidence,
                "input_margin_pct": in_margin,
                "output_margin_pct": out_margin,
                "recommended_action": (
                    "Мониторить при следующем economics snapshot. "
                    "Если Estimated — уточнить provider cost из официального прайса."
                ),
            })

        # MISSING_COST_BASIS (для non-Incomplete)
        if in_cost is None or out_cost is None:
            alerts.append({
                "alert_class": "MISSING_COST_BASIS",
                "severity": "MEDIUM",
                "model": model,
                "category": category,
                "confidence": confidence,
                "input_margin_pct": in_margin,
                "output_margin_pct": out_margin,
                "recommended_action": (
                    "Найти актуальный provider cost и дополнить economics matrix. "
                    "До обновления — трактовать как Incomplete по риску."
                ),
            })

        # ESTIMATED_ONLY_CATEGORY (один раз на категорию)
        if category in estimated_only_categories and category not in already_alerted_categories:
            already_alerted_categories.add(category)
            alerts.append({
                "alert_class": "ESTIMATED_ONLY_CATEGORY",
                "severity": "LOW",
                "model": None,
                "category": category,
                "confidence": "Estimated",
                "input_margin_pct": None,
                "output_margin_pct": None,
                "recommended_action": (
                    f"Вся категория '{category}' работает на proxy economics. "
                    "При доступности реальных provider costs — обновить до Exact."
                ),
            })

    return alerts


def _build_alerts_summary(alerts: list[dict]) -> dict:
    """Строит summary по alerts."""
    by_severity: dict[str, int] = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    by_class: dict[str, int] = {}
    for a in alerts:
        sev = a.get("severity", "LOW")
        cls = a.get("alert_class", "UNKNOWN")
        by_severity[sev] = by_severity.get(sev, 0) + 1
        by_class[cls] = by_class.get(cls, 0) + 1
    return {
        "total_alerts": len(alerts),
        "critical": by_severity["CRITICAL"],
        "high": by_severity["HIGH"],
        "medium": by_severity["MEDIUM"],
        "low": by_severity["LOW"],
        "by_class": by_class,
        "has_blocking": by_severity["CRITICAL"] > 0 or by_severity["HIGH"] > 0,
    }


@router.get("/operator/margin-alerts")
async def get_operator_margin_alerts(
    _current_user=Depends(get_current_user),
    _operator_secret: None = Depends(_require_operator_secret),
    severity: Optional[str] = Query(None, description="Фильтр по severity: CRITICAL/HIGH/MEDIUM/LOW"),
    alert_class: Optional[str] = Query(None, description="Фильтр по alert_class"),
):
    """Оператор-only margin alerts по snapshot economics. Требует X-Operator-Secret."""
    model_rows = _load_operator_economics_model_rows()
    alerts = _evaluate_margin_alerts(model_rows)

    # Фильтры
    if severity:
        alerts = [a for a in alerts if a["severity"] == severity.upper()]
    if alert_class:
        alerts = [a for a in alerts if a["alert_class"] == alert_class.upper()]

    summary = _build_alerts_summary(alerts)

    return {
        "snapshot_date": OPERATOR_ECONOMICS_SNAPSHOT_DATE,
        "policy_doc": "docs/current/MARGIN_ALERT_POLICY.md",
        "summary": summary,
        "alerts": alerts,
    }


@router.get("/operator/economics-view")
async def get_operator_economics_view(
    _current_user=Depends(get_current_user),
    _operator_secret: None = Depends(_require_operator_secret),
):
    """Возвращает operator-only economics snapshot по моделям и категориям."""
    model_rows = _load_operator_economics_model_rows()
    category_rows = _build_operator_economics_category_rows(model_rows)
    summary = _build_operator_economics_summary(model_rows)

    return {
        "snapshot_date": OPERATOR_ECONOMICS_SNAPSHOT_DATE,
        "visibility": "operator-only",
        "calculation_mode": "snapshot-report",
        "calculation_basis": {
            "fixed_rub_per_credit": float(getattr(settings, "FIXED_RUB_PER_CREDIT", 85.0)),
            "fx_rub_per_usd_proxy": 90.0,
            "retail_formula": "rate_credits × 1_000_000 × FIXED_RUB_PER_CREDIT ÷ 90",
            "provider_formula": "cost_per_token × 1_000_000",
            "note": "Snapshot derived from live billing.public_model_tariff + live LiteLLM config at audit date.",
        },
        "summary": summary,
        "category_rows": category_rows,
        "model_rows": model_rows,
        "source_docs": [
            "docs/current/PROVIDER_ECONOMICS_SOURCE_MAP.md",
            "docs/current/PROVIDER_ECONOMICS_REPORT.md",
            "docs/current/PROVIDER_ECONOMICS_CONFIDENCE_MATRIX.md",
        ],
    }


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

    return {
        "logs": [
            {
                "id": str(r.id),
                "created_at": r.created_at.isoformat(),
                "model": r.public_model_name or "",
                "provider": r.provider or "",
                "api_key_prefix": (r.api_key_hash or "")[:12] + "...",
                "input_tokens": r.input_tokens,
                "output_tokens": r.output_tokens,
                "charged_credits": float(r.charged_credits),
                "loyalty_discount_percent": float(r.loyalty_discount_percent),
                "raw_cost_usd": float(r.raw_provider_cost_usd) if r.raw_provider_cost_usd else None,
                "spend_log_id": r.litellm_spend_log_id,
            }
            for r in rows
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page if total > 0 else 1,
    }
