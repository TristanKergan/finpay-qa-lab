import allure
import pytest

from tests.api_client.finpay_api import FinPayApiClient


@allure.epic("Simulated Payment Provider")
@allure.feature("Provider Mock Processing Scenarios")
class TestMockPaymentApi:

    @allure.story("Scenario: SUCCESS")
    @pytest.mark.api
    def test_mock_payment_success(self, api_client: FinPayApiClient):
        payload = {"transaction_id": "txn_mock_001", "amount": 100.0, "currency": "USD", "scenario": "SUCCESS"}
        res = api_client.mock_process_payment(payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "SUCCESS"
        assert "event_id" in data
        assert "signature" in data

    @allure.story("Scenario: FAILED")
    @pytest.mark.api
    def test_mock_payment_failed(self, api_client: FinPayApiClient):
        payload = {"transaction_id": "txn_mock_002", "amount": 100.0, "currency": "USD", "scenario": "FAILED"}
        res = api_client.mock_process_payment(payload)
        assert res.status_code == 200
        assert res.json()["status"] == "FAILED"

    @allure.story("Scenario: TIMEOUT")
    @pytest.mark.api
    def test_mock_payment_timeout(self, api_client: FinPayApiClient):
        payload = {"transaction_id": "txn_mock_003", "amount": 100.0, "currency": "USD", "scenario": "TIMEOUT"}
        res = api_client.mock_process_payment(payload)
        assert res.status_code == 504
        assert "timeout" in res.json().get("detail", "").lower()
