import json
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    ENVIRONMENT: str = "development"
    APP_NAME: str = "FinPay QA Lab"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///finpay.db"

    # JWT & Auth
    JWT_SECRET_KEY: str = "super-secret-finpay-jwt-key-for-qa-testing-change-in-production-12345"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    MAX_FAILED_LOGIN_ATTEMPTS: int = 5

    # Server & CORS
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    FRONTEND_PORT: int = 3000
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
    ]

    # External Provider Mock
    WEBHOOK_SECRET: str = "payment-provider-hmac-secret-finpay-2026"

    # Exchange rates relative to USD (Base: USD = 1.0)
    EXCHANGE_RATES: dict = {
        "USD": 1.0,
        "EUR": 0.92,
        "UAH": 39.5,
    }

    # ==========================================
    # BUG_MODE Settings
    # ==========================================
    BUG_MODE: bool = False
    BUG_001_DUPLICATE_TRANSFER: bool = False
    BUG_002_DUPLICATE_WEBHOOK: bool = False
    BUG_003_EXPIRED_TOKEN_ALLOWED: bool = False
    BUG_004_NEGATIVE_TRANSFER_ALLOWED: bool = False
    BUG_005_PAGINATION_DUPLICATES: bool = False
    BUG_006_SELF_TRANSFER_ALLOWED: bool = False
    BUG_007_WRONG_CURRENCY_RATE: bool = False
    BUG_008_TRANSACTION_STUCK_PENDING: bool = False
    BUG_009_LOCKED_USER_CAN_LOGIN: bool = False
    BUG_010_UI_BALANCE_NOT_REFRESHED: bool = False

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                return [i.strip() for i in v.split(",") if i.strip()]
        return v

    def is_bug_active(self, bug_code: str) -> bool:
        """Check if a specific bug is enabled globally or individually."""
        if self.BUG_MODE:
            return True
        attr = f"BUG_{bug_code}"
        return getattr(self, attr, False)


settings = Settings()
