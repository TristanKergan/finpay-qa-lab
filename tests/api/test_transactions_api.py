import allure
import pytest

from tests.api_client.finpay_api import FinPayApiClient
from tests.config.settings import test_settings
from tests.schemas.api_schemas import TransactionListSchema


@allure.epic("Transactions")
@allure.feature("Transaction Ledger & History")
class TestTransactionsApi:

    @allure.story("Positive: Paginated Transactions Listing")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.api
    def test_list_transactions_pagination(self, auth_client_john: FinPayApiClient):
        res = auth_client_john.get_transactions({"page": 1, "page_size": 2})
        assert res.status_code == 200
        data = res.json()
        TransactionListSchema.model_validate(data)
        assert data["page"] == 1
        assert data["page_size"] == 2
        assert len(data["items"]) <= 2

    @allure.story("Positive: Filter Transactions by Status")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    def test_filter_transactions_by_status(self, auth_client_john: FinPayApiClient):
        res = auth_client_john.get_transactions({"status": "SUCCESS"})
        assert res.status_code == 200
        data = res.json()
        for item in data["items"]:
            assert item["status"] == "SUCCESS"

    @allure.story("Positive: Filter Transactions by Currency")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    def test_filter_transactions_by_currency(self, auth_client_john: FinPayApiClient):
        res = auth_client_john.get_transactions({"currency": "USD"})
        assert res.status_code == 200
        data = res.json()
        for item in data["items"]:
            assert item["currency"] == "USD"

    @allure.story("Security: IDOR Access Prevention on Transactions")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.api
    def test_unauthorized_transaction_access_idor(
        self,
        auth_client_jane: FinPayApiClient,
        auth_client_qa: FinPayApiClient
    ):
        # Create transfer from QA to John (Jane is NOT involved)
        res = auth_client_qa.create_transfer({
            "receiver_email": test_settings.USER_JOHN_EMAIL,
            "currency": "USD",
            "amount": 10.0,
            "description": "Private QA Transfer"
        })
        assert res.status_code == 201
        txn_id = res.json()["transaction_id"]

        # Jane tries to access this private transaction
        idor_res = auth_client_jane.get_transaction(txn_id)
        assert idor_res.status_code == 403, f"Expected 403 Forbidden for IDOR, got {idor_res.status_code}"

    @allure.story("Negative: Transaction Not Found (404)")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    def test_get_non_existent_transaction(self, auth_client_john: FinPayApiClient):
        res = auth_client_john.get_transaction("non-existent-uuid-000000000000")
        assert res.status_code == 404
