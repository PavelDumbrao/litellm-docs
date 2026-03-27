"""ProAICommunity Billing Portal."""
import json
import logging
import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager

# Настройка логирования — INFO для наших модулей
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.billing import router as billing_router
from app.api.keys import router as keys_router
from app.api.webhook import router as webhook_router
from app.workers.usage_sync import run_usage_sync, worker_router
from app.core.config import settings

logger = logging.getLogger(__name__)

DEPLOY_META_PATH = Path(__file__).resolve().parents[1] / ".deploy-release.json"


def _load_deploy_revision() -> dict:
    """Возвращает release-backed revision metadata текущего deploy."""
    if not DEPLOY_META_PATH.is_file():
        return {
            "traceability": "missing",
            "model": "release-backed",
            "commit": None,
            "repo": None,
            "branch": None,
            "deployed_at": None,
            "canonical_vps_path": "/opt/billing-portal",
            "detail": f"Revision file not found: {DEPLOY_META_PATH}",
        }

    try:
        payload = json.loads(DEPLOY_META_PATH.read_text())
    except Exception as error:
        logger.error(f"[REVISION] failed to read {DEPLOY_META_PATH}: {error}")
        return {
            "traceability": "invalid",
            "model": "release-backed",
            "commit": None,
            "repo": None,
            "branch": None,
            "deployed_at": None,
            "canonical_vps_path": "/opt/billing-portal",
            "detail": str(error),
        }

    payload.setdefault("traceability", "ok")
    payload.setdefault("model", "release-backed")
    payload.setdefault("canonical_vps_path", "/opt/billing-portal")
    return payload

# ---------------------------------------------------------------------------
# Cron scheduler — запускает usage sync каждые 10 минут
# Чтобы отключить: установить USAGE_SYNC_INTERVAL_MINUTES=0 в .env
# ---------------------------------------------------------------------------
scheduler = AsyncIOScheduler(timezone="UTC")


async def _scheduled_usage_sync():
    """Периодический запуск usage worker."""
    try:
        stats = await run_usage_sync()
        if stats["processed"] > 0:
            logger.info(f"[CRON] usage_sync: {stats}")
    except Exception as e:
        logger.error(f"[CRON] usage_sync error: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan: запускаем и останавливаем scheduler."""
    interval = getattr(settings, "USAGE_SYNC_INTERVAL_MINUTES", 10)
    if interval and int(interval) > 0:
        scheduler.add_job(
            _scheduled_usage_sync,
            trigger="interval",
            minutes=int(interval),
            id="usage_sync",
            replace_existing=True,
            max_instances=1,
        )
        scheduler.start()
        logger.info(f"[CRON] usage_sync scheduled every {interval} min")
    else:
        logger.info("[CRON] usage_sync disabled (USAGE_SYNC_INTERVAL_MINUTES=0)")
    yield
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("[CRON] scheduler stopped")


def _validate_env() -> None:
    """Fail-fast проверка обязательных переменных окружения."""
    required = {
        "JWT_SECRET_KEY": settings.JWT_SECRET_KEY,
        "DATABASE_URL": settings.DATABASE_URL,
        "PRODAMUS_SECRET_KEY": settings.PRODAMUS_SECRET_KEY,
    }
    missing = [key for key, val in required.items() if not val or not str(val).strip()]
    if missing:
        print(f"[FATAL] Не заданы обязательные переменные окружения: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)


_validate_env()

app = FastAPI(
    title="ProAICommunity Billing Portal",
    description="API для управления балансом, пакетами и платежами.",
    version="1.0.0",
    lifespan=lifespan,
)

ALLOWED_ORIGINS = [
    "https://billing.proaicommunity.online",
    "https://proaicommunity.online",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

app.include_router(auth_router, prefix="/api/auth")
app.include_router(billing_router, prefix="/api/billing")
app.include_router(keys_router, prefix="/api/api-keys")
app.include_router(webhook_router, prefix="/api/billing/webhook")
app.include_router(worker_router, prefix="/api/worker")


@app.get("/health", tags=["system"])
async def health():
    """Health check endpoint."""
    revision = _load_deploy_revision()
    return {
        "status": "ok",
        "service": "billing-portal",
        "revision": revision.get("commit"),
        "traceability": revision.get("traceability"),
        "deploy_model": revision.get("model"),
    }


@app.get("/api/system/revision", tags=["system"])
async def system_revision():
    """Явный revision endpoint для runtime traceability."""
    return _load_deploy_revision()


# ---------------------------------------------------------------------------
# Static files + SPA fallback
# ---------------------------------------------------------------------------
from fastapi import HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "static")

if os.path.isdir(STATIC_DIR):
    assets_dir = os.path.join(STATIC_DIR, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    SPA_ROUTES = {"login", "register", "billing", "api-keys", "usage", "models", "dashboard", "orders"}

    @app.get("/{full_path:path}")
    async def spa_fallback(full_path: str):
        if full_path.startswith(("api/", "assets/", "docs", "openapi", "health")):
            raise HTTPException(status_code=404, detail="Not Found")
        if not full_path or full_path in SPA_ROUTES:
            index = os.path.join(STATIC_DIR, "index.html")
            if os.path.isfile(index):
                return FileResponse(index, media_type="text/html")
        raise HTTPException(status_code=404, detail="Not Found")
else:
    logger.warning(f"Static dir not found at {STATIC_DIR}")
