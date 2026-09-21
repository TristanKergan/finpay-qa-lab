import uuid

import allure
import pytest
from sqlalchemy import select

from backend.app.core.database import AsyncSessionLocal
from backend.app.models import Transaction
from tests.api_client.finpay_api import FinPayApiClient
from tests.config.settings import test_settings
from tests.factories.user_factory import TransferFactory
from tests.utils.db_helper import DbHelper


@allure.epic("Database & Data Integrity")
@allure.feature("Balance Conservation & ACID Transactions")
class TestDatabaseBalanceIntegrity:

    @allure.story("Integrity: Exact Balance Conservation on Transfer")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.database
    async def test_balance_conservation_after_transfer(self, auth_client_john: FinPayApiClient):
        sender_email = test_settings.USER_JOHN_EMAIL
        receiver_email = test_settings.USER_ALEX_EMAIL
        amount = 75.0
        currency = "USD"

        # 1. Fetch balances before
        sender_user = await DbHelper.get_user_by_email(sender_email)
        receiver_user = await DbHelper.get_user_by_email(receiver_email)
        assert sender_user and receiver_user

        sender_bal_before, _ = await DbHelper.get_wallet_balance(sender_user.id, currency)
        receiver_bal_before, _ = await DbHelper.get_wallet_balance(receiver_user.id, currency)

        # 2. Perform transfer via API
        idempotency_key = f"db_test_idem_{uuid.uuid4()}"
        res = auth_client_john.create_transfer(
            TransferFactory.build(
                receiver_email=receiver_email,
                amount=amount,
                currency=currency,
                idempotency_key=idempotency_key
            )
        )
        assert res.status_code == 201

        # 3. Direct SQL verification of balances
        sender_bal_after, _ = await DbHelper.get_wallet_balance(sender_user.id, currency)
        receiver_bal_after, _ = await DbHelper.get_wallet_balance(receiver_user.id, currency)

        assert round(sender_bal_after, 2) == round(sender_bal_before - amount, 2), "Sender balance not debited accurately"
        assert round(receiver_bal_after, 2) == round(receiver_bal_before + amount, 2), "Receiver balance not credited accurately"

        # 4. Direct SQL verification of transaction row
        async with AsyncSessionLocal() as session:
            txn_res = await session.execute(
                select(Transaction).where(Transaction.idempotency_key == idempotency_key)
            )
            txn = txn_res.scalar_one_or_none()
            assert txn is not None
            assert txn.status == "SUCCESS"
            assert txn.amount == amount
            assert txn.sender_id == sender_user.id
            assert txn.receiver_id == receiver_user.id

    @allure.story("Integrity: ACID Rollback on Transfer Rejection")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.database
    async def test_acid_rollback_on_failed_transfer(self, auth_client_john: FinPayApiClient):
        sender_email = test_settings.USER_JOHN_EMAIL
        sender_user = await DbHelper.get_user_by_email(sender_email)
        sender_bal_before, _ = await DbHelper.get_wallet_balance(sender_user.id, "USD")

        # Attempt transfer with overdraft
        res = auth_client_john.create_transfer(
            TransferFactory.build(
                receiver_email=test_settings.USER_JANE_EMAIL,
                amount=9999999.0,
                currency="USD"
            )
        )
        assert res.status_code == 400

        # Verify sender balance remained completely unchanged
        sender_bal_after, _ = await DbHelper.get_wallet_balance(sender_user.id, "USD")
        assert sender_bal_after == sender_bal_before
