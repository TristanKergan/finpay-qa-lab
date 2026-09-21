import os

from pydantic_settings import BaseSettings


class TestSettings(BaseSettings):
    BASE_URL: str = os.getenv("TEST_BASE_URL", "http://127.0.0.1:8000")
    FRONTEND_URL: str = os.getenv("TEST_FRONTEND_URL", "http://127.0.0.1:3000")
    DATABASE_URL: str = os.getenv("TEST_DATABASE_URL", "sqlite+aiosqlite:///finpay.db")

    # Pre-seeded test credentials
    USER_JOHN_EMAIL: str = "john.doe@example.com"
    USER_JOHN_PASSWORD: str = "Password123!"

    USER_JANE_EMAIL: str = "jane.smith@example.com"
    USER_JANE_PASSWORD: str = "Password123!"

    USER_ALEX_EMAIL: str = "alex.wilson@example.com"
    USER_ALEX_PASSWORD: str = "Password123!"

    USER_LOCKED_EMAIL: str = "locked.user@example.com"
    USER_LOCKED_PASSWORD: str = "Password123!"

    USER_QA_EMAIL: str = "qa.tester@example.com"
    USER_QA_PASSWORD: str = "Password123!"

    REQUEST_TIMEOUT: float = 10.0
    PLAYWRIGHT_HEADLESS: bool = True
    PLAYWRIGHT_SLOWMO: float = 0.0


test_settings = TestSettings()
