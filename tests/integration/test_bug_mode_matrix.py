import uuid
from datetime import datetime, timedelta, timezone

import allure
import pytest

from backend.app.core.config import settings
from backend.app.core.security import create_access_token
from backend.app.services.wallet_service import WalletService
from backend.app.services.webhook_service import WebhookService
from tests.api_client.finpay_api import FinPayApiClient
from tests.config.settings import test_settings


@allure.epic("Defect Detection Matrix (BUG_MODE)")
@allure.feature("Verification of 10 Realistic Fintech Defects")
class TestBugModeMatrix:

    @pytest.fixture(autouse=True)
    def reset_bug_mode(self, api_client: FinPayApiClient):
        """Ensure BUG_MODE is cleanly reset before and after every test."""
        api_client.set_debug_bugs({"reset_all": True, "BUG_MODE": False})
        yield
        api_client.set_debug_bugs({"reset_all": True, "BUG_MODE": False})
        for i in range(1, 11):
            # Reset any active flag in pytest process
            for attr in dir(settings):
                if attr.startswith(f"BUG_{i:03d}"):
                    setattr(settings, attr, False)

    @allure.story("BUG-001: Duplicate Transfer Detection")
    @pytest.mark.bug_mode
    def test_bug_001_duplicate_transfer_detection(self, auth_client_john: FinPayApiClient):
        idem_key = f"idem_bug001_{uuid.uuid4()}"
        payload = {
            "receiver_email": test_settings.USER_JANE_EMAIL,
            "amount": 10.0,
            "currency": "USD",
            "idempotency_key": idem_key
        }

        # Normal mode: second transfer is idempotent
        res1 = auth_client_john.create_transfer(payload)
        assert res1.status_code == 201
        res2 = auth_client_john.create_transfer(payload)
        assert res2.json()["transaction_id"] == res1.json()["transaction_id"]

        # Activate BUG_001
        auth_client_john.set_debug_bugs({"BUG_001_DUPLICATE_TRANSFER": True})
        res3 = auth_client_john.create_transfer(payload)
        # In BUG_001 mode, a second duplicate transaction is created instead of idempotent replay
        assert res3.status_code == 201
        assert res3.json()["transaction_id"] != res1.json()["transaction_id"], "BUG-001 reproduced: duplicate transfer executed"

    @allure.story("BUG-002: Duplicate Webhook Protection vs Bypass")
    @pytest.mark.bug_mode
    def test_bug_002_duplicate_webhook(self, auth_client_qa: FinPayApiClient):
        txn = auth_client_qa.create_transfer({
            "receiver_email": test_settings.USER_JANE_EMAIL,
            "amount": 15.0,
            "currency": "USD"
        }).json()
        txn_id = txn["transaction_id"]

        event_id = f"evt_bug002_{uuid.uuid4()}"
        ts = datetime.now(timezone.utc).isoformat()
        sig = WebhookService.generate_signature(event_id, txn_id, "SUCCESS", ts)
        payload = {"event_id": event_id, "transaction_id": txn_id, "status": "SUCCESS", "timestamp": ts, "signature": sig}

        # Normal mode: 2nd dispatch is ALREADY_PROCESSED
        r1 = auth_client_qa.post_webhook(payload)
        assert r1.json()["status"] == "PROCESSED"
        r2 = auth_client_qa.post_webhook(payload)
        assert r2.json()["status"] == "ALREADY_PROCESSED"

        # Activate BUG_002
        auth_client_qa.set_debug_bugs({"BUG_002_DUPLICATE_WEBHOOK": True})
        r3 = auth_client_qa.post_webhook(payload)
        assert r3.json()["status"] == "PROCESSED", "BUG-002 reproduced: duplicate webhook processed again"

    @allure.story("BUG-003: Expired Access Token Acceptance")
    @pytest.mark.bug_mode
    def test_bug_003_expired_token_allowed(self, api_client: FinPayApiClient):
        login_res = api_client.login(test_settings.USER_JOHN_EMAIL, test_settings.USER_JOHN_PASSWORD).json()
        john_id = login_res["user_id"]

        # Create an expired token for John Doe
        expired_token = create_access_token(
            subject=john_id,
            expires_delta=timedelta(seconds=-120),
            extra_claims={"email": test_settings.USER_JOHN_EMAIL, "role": "user"}
        )

        # Normal mode: expired token is rejected with 401
        api_client.set_token(expired_token)
        r_normal = api_client.get("/api/v1/users/me")
        assert r_normal.status_code == 401

        # BUG_003 mode: expired token is accepted (200)
        api_client.set_debug_bugs({"BUG_003_EXPIRED_TOKEN_ALLOWED": True})
        r_bug = api_client.get("/api/v1/users/me")
        assert r_bug.status_code == 200, "BUG-003 reproduced: expired token was erroneously accepted"

    @allure.story("BUG-004: Negative Amount Transfer")
    @pytest.mark.bug_mode
    def test_bug_004_negative_transfer(self, auth_client_john: FinPayApiClient):
        payload = {
            "receiver_email": test_settings.USER_JANE_EMAIL,
            "amount": -50.0,
            "currency": "USD"
        }
        # Normal mode: rejected with 400
        r_normal = auth_client_john.create_transfer(payload)
        assert r_normal.status_code in [400, 422]

        # BUG_004 mode: accepted!
        auth_client_john.set_debug_bugs({"BUG_004_NEGATIVE_TRANSFER_ALLOWED": True})
        r_bug = auth_client_john.create_transfer(payload)
        assert r_bug.status_code == 201, "BUG-004 reproduced: negative amount transfer allowed"

    @allure.story("BUG-005: Pagination Duplicates on Page Boundaries")
    @pytest.mark.bug_mode
    def test_bug_005_pagination_duplicates(self, auth_client_john: FinPayApiClient):
        # Normal mode: page 1 and page 2 have distinct items
        p1 = auth_client_john.get_transactions(params={"page": 1, "page_size": 3}).json()
        p2 = auth_client_john.get_transactions(params={"page": 2, "page_size": 3}).json()

        if len(p1["items"]) >= 3 and len(p2["items"]) >= 1:
            p1_ids = {t["id"] for t in p1["items"]}
            p2_ids = {t["id"] for t in p2["items"]}
            assert len(p1_ids & p2_ids) == 0, "Normal mode should have no overlap across pages"

            # Activate BUG_005
            auth_client_john.set_debug_bugs({"BUG_005_PAGINATION_DUPLICATES": True})
            p2_bug = auth_client_john.get_transactions(params={"page": 2, "page_size": 3}).json()
            p2_bug_ids = {t["id"] for t in p2_bug["items"]}
            overlap = p1_ids & p2_bug_ids
            assert len(overlap) > 0, "BUG-005 reproduced: duplicate transaction found across page boundaries"

    @allure.story("BUG-006: Self-Transfer Prohibition vs Allowed")
    @pytest.mark.bug_mode
    def test_bug_006_self_transfer(self, auth_client_john: FinPayApiClient):
        payload = {
            "receiver_email": test_settings.USER_JOHN_EMAIL,
            "amount": 10.0,
            "currency": "USD"
        }
        # Normal: blocked
        r_normal = auth_client_john.create_transfer(payload)
        assert r_normal.status_code == 400

        # BUG_006 mode: allowed
        auth_client_john.set_debug_bugs({"BUG_006_SELF_TRANSFER_ALLOWED": True})
        r_bug = auth_client_john.create_transfer(payload)
        assert r_bug.status_code == 201, "BUG-006 reproduced: self-transfer allowed"

    @allure.story("BUG-007: Wrong Currency Conversion Rate")
    @pytest.mark.bug_mode
    def test_bug_007_currency_rate_calculation(self, api_client: FinPayApiClient):
        # Base: USD = 1.0, EUR = 0.92.
        # Converting 100.0 EUR to USD:
        # Standard: 100.0 * (1.0 / 0.92) = 108.70 USD
        amt_normal, rate_normal = WalletService.convert_currency(100.0, "EUR", "USD")
        assert amt_normal == 108.70
        assert rate_normal == 1.0870

        # BUG_007: Inverted exchange rate: from_rate / to_rate = 0.92 / 1.0 = 0.92
        # Buggy result: 100.0 * 0.92 = 92.00 USD
        api_client.set_debug_bugs({"BUG_007_WRONG_CURRENCY_RATE": True})
        setattr(settings, "BUG_007_WRONG_CURRENCY_RATE", True)
        amt_bug, rate_bug = WalletService.convert_currency(100.0, "EUR", "USD")
        assert amt_bug == 92.00, "BUG-007 reproduced: inverted exchange rate applied"

    @allure.story("BUG-008: Payment Webhook Stuck in Pending")
    @pytest.mark.bug_mode
    def test_bug_008_transaction_stuck_pending(self, auth_client_qa: FinPayApiClient):
        import asyncio

        from backend.app.core.database import AsyncSessionLocal
        from backend.app.models import Transaction

        qa_user_id = auth_client_qa.get("/api/v1/users/me").json()["id"]

        async def insert_pending_txn():
            async with AsyncSessionLocal() as session:
                t = Transaction(
                    sender_id=qa_user_id,
                    amount=20.0,
                    currency="USD",
                    converted_amount=20.0,
                    target_currency="USD",
                    exchange_rate=1.0,
                    status="PENDING",
                    idempotency_key=f"pending_{uuid.uuid4().hex}"
                )
                session.add(t)
                await session.commit()
                return t.id

        txn_id = asyncio.run(insert_pending_txn())
        txn2_id = asyncio.run(insert_pending_txn())

        event_id = f"evt_bug008_{uuid.uuid4()}"
        ts = datetime.now(timezone.utc).isoformat()
        sig = WebhookService.generate_signature(event_id, txn_id, "SUCCESS", ts)
        payload = {"event_id": event_id, "transaction_id": txn_id, "status": "SUCCESS", "timestamp": ts, "signature": sig}

        # Normal mode: SUCCESS webhook sets transaction status to SUCCESS
        r1 = auth_client_qa.post_webhook(payload)
        assert r1.status_code == 200
        assert auth_client_qa.get_transaction(txn_id).json()["status"] == "SUCCESS"

        # Activate BUG_008: Webhook received but status remains PENDING
        auth_client_qa.set_debug_bugs({"BUG_008_TRANSACTION_STUCK_PENDING": True})
        event2_id = f"evt_bug008_2_{uuid.uuid4()}"
        ts2 = datetime.now(timezone.utc).isoformat()
        sig2 = WebhookService.generate_signature(event2_id, txn2_id, "SUCCESS", ts2)
        r2 = auth_client_qa.post_webhook({"event_id": event2_id, "transaction_id": txn2_id, "status": "SUCCESS", "timestamp": ts2, "signature": sig2})
        assert r2.status_code == 200

        # In BUG_008 mode, transaction status was not updated and remained PENDING
        txn2_state = auth_client_qa.get_transaction(txn2_id).json()
        assert txn2_state["status"] == "PENDING", "BUG-008 reproduced: transaction status stuck in PENDING"

    @allure.story("BUG-009: Locked User Login")
    @pytest.mark.bug_mode
    def test_bug_009_locked_user_login(self, api_client: FinPayApiClient):
        # Normal: locked user cannot login (403)
        r_normal = api_client.login(test_settings.USER_LOCKED_EMAIL, test_settings.USER_LOCKED_PASSWORD)
        assert r_normal.status_code == 403

        # BUG_009 mode: locked user CAN login (200)
        api_client.set_debug_bugs({"BUG_009_LOCKED_USER_CAN_LOGIN": True})
        r_bug = api_client.login(test_settings.USER_LOCKED_EMAIL, test_settings.USER_LOCKED_PASSWORD)
        assert r_bug.status_code == 200, "BUG-009 reproduced: locked user successfully logged in"

    @allure.story("BUG-010: UI Balance Not Refreshed Flag")
    @pytest.mark.bug_mode
    def test_bug_010_ui_balance_refresh_suppression(self, auth_client_john: FinPayApiClient):
        payload = {
            "receiver_email": test_settings.USER_JANE_EMAIL,
            "amount": 10.0,
            "currency": "USD"
        }
        # Normal mode: suppress_refresh is False
        r_normal = auth_client_john.create_transfer(payload)
        assert r_normal.status_code == 201
        assert r_normal.json().get("suppress_refresh") is False

        # BUG_010 mode: suppress_refresh is True, preventing frontend from invalidating wallet cache
        auth_client_john.set_debug_bugs({"BUG_010_UI_BALANCE_NOT_REFRESHED": True})
        r_bug = auth_client_john.create_transfer(payload)
        assert r_bug.status_code == 201
        assert r_bug.json().get("suppress_refresh") is True, "BUG-010 reproduced: suppress_refresh flag is active"
