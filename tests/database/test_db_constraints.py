import uuid
import pytest
import allure
from sqlalchemy.exc import IntegrityError
from backend.app.core.database import AsyncSessionLocal
from backend.app.models import User, Wallet, Transaction


@allure.epic("Database & Data Integrity")
@allure.feature("Database Schema Constraints & Indexes")
class TestDatabaseConstraints:

    @allure.story("Constraint: Unique Currency Wallet per User")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.database
    async def test_unique_user_currency_constraint(self):
        unique_email = f"db_constraint_{uuid.uuid4().hex[:8]}@example.com"
        async with AsyncSessionLocal() as session:
            # Create a test user
            u = User(
                email=unique_email,
                hashed_password="hash",
                full_name="Constraint Tester",
                status="ACTIVE"
            )
            session.add(u)
            await session.flush()

            # Add first USD wallet
            w1 = Wallet(user_id=u.id, currency="USD", balance=100.0, available_balance=100.0)
            session.add(w1)
            await session.commit()

        # Attempt adding a duplicate USD wallet for the same user
        with pytest.raises(IntegrityError):
            async with AsyncSessionLocal() as session:
                w2 = Wallet(user_id=u.id, currency="USD", balance=200.0, available_balance=200.0)
                session.add(w2)
                await session.commit()

    @allure.story("Constraint: Unique Idempotency Key in Transactions")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.database
    async def test_unique_idempotency_key_constraint(self):
        fixed_key = f"db_unique_idem_key_{uuid.uuid4().hex}"
        async with AsyncSessionLocal() as session:
            t1 = Transaction(
                amount=10.0,
                currency="USD",
                converted_amount=10.0,
                target_currency="USD",
                exchange_rate=1.0,
                status="SUCCESS",
                idempotency_key=fixed_key
            )
            session.add(t1)
            await session.commit()

        # Attempt adding duplicate idempotency_key
        with pytest.raises(IntegrityError):
            async with AsyncSessionLocal() as session:
                t2 = Transaction(
                    amount=20.0,
                    currency="USD",
                    converted_amount=20.0,
                    target_currency="USD",
                    exchange_rate=1.0,
                    status="SUCCESS",
                    idempotency_key=fixed_key
                )
                session.add(t2)
                await session.commit()
