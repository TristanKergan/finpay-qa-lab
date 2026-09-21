import pytest
import allure
from tests.api_client.finpay_api import FinPayApiClient
from tests.schemas.api_schemas import WalletSummarySchema


@allure.epic("Wallet & Treasury")
@allure.feature("Multi-Currency Balances")
class TestWalletApi:

    @allure.story("Positive: Retrieve Wallet Summary for Authenticated User")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.api
    def test_get_wallet_summary_success(self, auth_client_john: FinPayApiClient):
        res = auth_client_john.get_wallet()
        assert res.status_code == 200
        data = res.json()
        WalletSummarySchema.model_validate(data)
        
        currencies = [w["currency"] for w in data["wallets"]]
        assert "USD" in currencies
        assert "EUR" in currencies
        assert "UAH" in currencies
        assert data["total_balance_usd"] > 0

    @allure.story("Negative: Unauthorized Access to Wallet")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.api
    def test_get_wallet_unauthorized(self, api_client: FinPayApiClient):
        api_client.clear_token()
        res = api_client.get_wallet()
        assert res.status_code == 401
