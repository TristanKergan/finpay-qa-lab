import uuid
from datetime import datetime, timezone

import allure
import pytest

from backend.app.services.webhook_service import WebhookService
from tests.api_client.finpay_api import FinPayApiClient
from tests.config.settings import test_settings


@allure.epic("Integrations & Webhooks")
@allure.feature("Payment Provider Webhooks")
class TestWebhooksApi:

    @allure.story("Positive: Successful Webhook Processing")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.api
    def test_process_valid_payment_webhook(self, auth_client_qa: FinPayApiClient):
        # 1. Create a transaction
        txn_res = auth_client_qa.create_transfer({
            "receiver_email": test_settings.USER_JANE_EMAIL,
            "amount": 20.0,
            "currency": "USD"
        })
        assert txn_res.status_code == 201
        txn_id = txn_res.json()["transaction_id"]

        # 2. Craft valid webhook payload
        event_id = f"evt_{uuid.uuid4()}"
        timestamp = datetime.now(timezone.utc).isoformat()
        status_val = "SUCCESS"
        signature = WebhookService.generate_signature(event_id, txn_id, status_val, timestamp)

        payload = {
            "event_id": event_id,
            "transaction_id": txn_id,
            "status": status_val,
            "timestamp": timestamp,
            "signature": signature
        }

        # 3. Post webhook
        res = auth_client_qa.post_webhook(payload)
        assert res.status_code == 200
        assert res.json()["status"] == "PROCESSED"

    @allure.story("Security: Duplicate Webhook Idempotency Protection")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.api
    def test_duplicate_webhook_protection(self, auth_client_qa: FinPayApiClient):
        txn_res = auth_client_qa.create_transfer({
            "receiver_email": test_settings.USER_JANE_EMAIL,
            "amount": 30.0,
            "currency": "USD"
        })
        txn_id = txn_res.json()["transaction_id"]

        event_id = f"evt_dup_{uuid.uuid4()}"
        timestamp = datetime.now(timezone.utc).isoformat()
        signature = WebhookService.generate_signature(event_id, txn_id, "SUCCESS", timestamp)

        payload = {
            "event_id": event_id,
            "transaction_id": txn_id,
            "status": "SUCCESS",
            "timestamp": timestamp,
            "signature": signature
        }

        # First dispatch
        res1 = auth_client_qa.post_webhook(payload)
        assert res1.status_code == 200
        assert res1.json()["status"] == "PROCESSED"

        # Replay duplicate webhook
        res2 = auth_client_qa.post_webhook(payload)
        assert res2.status_code == 200
        assert res2.json()["status"] == "ALREADY_PROCESSED"
        assert "duplicate" in res2.json().get("message", "").lower()

    @allure.story("Security: Reject Webhook with Invalid Signature")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.api
    def test_invalid_webhook_signature(self, api_client: FinPayApiClient):
        payload = {
            "event_id": f"evt_fake_{uuid.uuid4()}",
            "transaction_id": "fake_txn_id",
            "status": "SUCCESS",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "signature": "invalid_tampered_signature_9999"
        }
        res = api_client.post_webhook(payload)
        assert res.status_code == 401
        assert "invalid webhook signature" in res.json().get("detail", "").lower()
