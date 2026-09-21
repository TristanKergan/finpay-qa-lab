import uuid

import allure
import pytest

from tests.api_client.finpay_api import FinPayApiClient
from tests.config.settings import test_settings
from tests.factories.user_factory import TransferFactory
from tests.schemas.api_schemas import TransferSchema


@allure.epic("Transfers")
@allure.feature("Money Transfer Engine")
class TestTransfersApi:

    @allure.story("Positive: Successful Transfer Between Users")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.api
    def test_transfer_success_usd(self, auth_client_john: FinPayApiClient):
        payload = TransferFactory.build(
            receiver_email=test_settings.USER_JANE_EMAIL,
            amount=50.0,
            currency="USD",
            description="API test transfer"
        )
        res = auth_client_john.create_transfer(payload)
        assert res.status_code == 201
        data = res.json()
        TransferSchema.model_validate(data)
        assert data["status"] == "SUCCESS"
        assert data["amount"] == 50.0
        assert data["currency"] == "USD"
        assert data["sender_email"] == test_settings.USER_JOHN_EMAIL
        assert data["receiver_email"] == test_settings.USER_JANE_EMAIL

    @allure.story("Negative: Transfer More Than Available Balance")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.api
    def test_transfer_insufficient_balance(self, auth_client_john: FinPayApiClient):
        payload = TransferFactory.build(
            receiver_email=test_settings.USER_JANE_EMAIL,
            amount=9999999.0,
            currency="USD"
        )
        res = auth_client_john.create_transfer(payload)
        assert res.status_code == 400
        assert "insufficient" in res.json().get("detail", "").lower()

    @allure.story("Negative: Transfer to Self Disallowed")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.api
    def test_transfer_self_disallowed(self, auth_client_john: FinPayApiClient):
        payload = TransferFactory.build(
            receiver_email=test_settings.USER_JOHN_EMAIL,
            amount=10.0,
            currency="USD"
        )
        res = auth_client_john.create_transfer(payload)
        assert res.status_code == 400
        assert "yourself" in res.json().get("detail", "").lower()

    @allure.story("Negative: Transfer Zero Amount")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    def test_transfer_zero_amount(self, auth_client_john: FinPayApiClient):
        payload = TransferFactory.build(
            receiver_email=test_settings.USER_JANE_EMAIL,
            amount=0.0,
            currency="USD"
        )
        res = auth_client_john.create_transfer(payload)
        assert res.status_code in [400, 422]

    @allure.story("Negative: Transfer Negative Amount")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.api
    def test_transfer_negative_amount(self, auth_client_john: FinPayApiClient):
        payload = TransferFactory.build(
            receiver_email=test_settings.USER_JANE_EMAIL,
            amount=-25.0,
            currency="USD"
        )
        res = auth_client_john.create_transfer(payload)
        assert res.status_code in [400, 422]

    @allure.story("Negative: Transfer to Non-Existent Receiver")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    def test_transfer_non_existent_receiver(self, auth_client_john: FinPayApiClient):
        payload = TransferFactory.build(
            receiver_email="nonexistent_user_9999@finpay.io",
            amount=10.0,
            currency="USD"
        )
        res = auth_client_john.create_transfer(payload)
        assert res.status_code == 404
        assert "not found" in res.json().get("detail", "").lower()

    @allure.story("Idempotency: Duplicate Transfer Request Protected")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.api
    def test_transfer_idempotency_protection(self, auth_client_john: FinPayApiClient):
        idempotency_key = f"test_idem_{uuid.uuid4()}"

        payload = TransferFactory.build(
            receiver_email=test_settings.USER_JANE_EMAIL,
            amount=15.0,
            currency="USD",
            idempotency_key=idempotency_key
        )

        # 1st request
        res1 = auth_client_john.create_transfer(payload)
        assert res1.status_code == 201
        txn_id_1 = res1.json()["transaction_id"]

        # 2nd request with identical idempotency key
        res2 = auth_client_john.create_transfer(payload)
        assert res2.status_code in [200, 201]
        data2 = res2.json()
        assert data2["transaction_id"] == txn_id_1
        assert "idempotent" in data2.get("message", "").lower()
