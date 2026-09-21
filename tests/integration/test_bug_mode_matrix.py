import uuid
from datetime import datetime, timezone
import pytest
import allure
from backend.app.core.config import settings
from tests.api_client.finpay_api import FinPayApiClient
from tests.config.settings import test_settings
from backend.app.services.webhook_service import WebhookService
from tests.factories.user_factory import UserFactory


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
            key = f"BUG_{i:03d}"
            # Reset any active flag
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
