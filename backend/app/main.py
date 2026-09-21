from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api import mock_provider
from backend.app.api.v1 import (
    auth,
    cards,
    notifications,
    transactions,
    transfers,
    users,
    wallet,
    webhooks,
)
from backend.app.core.config import settings
from backend.app.core.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB schemas on startup
    await init_db()
    yield


app = FastAPI(
    title="FinPay QA Lab API",
    version="1.0.0",
    description="Production-grade Fintech REST API engineered for comprehensive QA Automation testing.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS Configuration
origins = settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Versioned API Routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(wallet.router, prefix="/api/v1")
app.include_router(transfers.router, prefix="/api/v1")
app.include_router(transactions.router, prefix="/api/v1")
app.include_router(cards.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")
app.include_router(webhooks.router, prefix="/api/v1")

# Also include unversioned /api/* aliases for direct compatibility
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(wallet.router, prefix="/api")
app.include_router(transfers.router, prefix="/api")
app.include_router(transactions.router, prefix="/api")
app.include_router(cards.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")
app.include_router(webhooks.router, prefix="/api")

# Register Simulated Payment Provider
app.include_router(mock_provider.router)


@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "bug_mode": settings.BUG_MODE,
        "active_defects": {
            "BUG_001_DUPLICATE_TRANSFER": settings.is_bug_active("001_DUPLICATE_TRANSFER"),
            "BUG_002_DUPLICATE_WEBHOOK": settings.is_bug_active("002_DUPLICATE_WEBHOOK"),
            "BUG_003_EXPIRED_TOKEN_ALLOWED": settings.is_bug_active("003_EXPIRED_TOKEN_ALLOWED"),
            "BUG_004_NEGATIVE_TRANSFER_ALLOWED": settings.is_bug_active("004_NEGATIVE_TRANSFER_ALLOWED"),
            "BUG_005_PAGINATION_DUPLICATES": settings.is_bug_active("005_PAGINATION_DUPLICATES"),
            "BUG_006_SELF_TRANSFER_ALLOWED": settings.is_bug_active("006_SELF_TRANSFER_ALLOWED"),
            "BUG_007_WRONG_CURRENCY_RATE": settings.is_bug_active("007_WRONG_CURRENCY_RATE"),
            "BUG_008_TRANSACTION_STUCK_PENDING": settings.is_bug_active("008_TRANSACTION_STUCK_PENDING"),
            "BUG_009_LOCKED_USER_CAN_LOGIN": settings.is_bug_active("009_LOCKED_USER_CAN_LOGIN"),
            "BUG_010_UI_BALANCE_NOT_REFRESHED": settings.is_bug_active("010_UI_BALANCE_NOT_REFRESHED"),
        }
    }


@app.post("/api/debug/bugs", tags=["QA Testing Hooks"])
async def set_bug_mode(payload: dict[str, Any]):
    """Dynamic test hook for QA automation to toggle BUG_MODE during test runs."""
    if payload.get("reset_all") or payload.get("BUG_MODE") is False:
        settings.BUG_MODE = False
        for attr in dir(settings):
            if attr.startswith("BUG_"):
                setattr(settings, attr, False)

    for key, value in payload.items():
        if hasattr(settings, key) and key != "reset_all":
            setattr(settings, key, bool(value))
    return {
        "message": "Bug mode flags updated",
        "BUG_MODE": settings.BUG_MODE,
        "flags": {
            k: getattr(settings, k)
            for k in dir(settings)
            if k.startswith("BUG_")
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app.main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.DEBUG
    )
