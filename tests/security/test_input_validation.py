import allure
import pytest

from tests.api_client.finpay_api import FinPayApiClient
from tests.config.settings import test_settings
from tests.factories.user_factory import TransferFactory


@allure.epic("Security Testing")
@allure.feature("Input Sanitization & Injection Resistance")
class TestInputValidation:

    @allure.story("Injection: SQL Injection Resistance in Description & Search")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    @pytest.mark.parametrize("sqli_payload", [
        "' OR '1'='1",
        "'; DROP TABLE users; --",
        "1' UNION SELECT null, null, null--",
        "admin' --",
    ])
    def test_sqli_payload_resistance(self, auth_client_john: FinPayApiClient, sqli_payload: str):
        # Test in transfer description
        res = auth_client_john.create_transfer(
            TransferFactory.build(
                receiver_email=test_settings.USER_JANE_EMAIL,
                amount=1.0,
                currency="USD",
                description=sqli_payload
            )
        )
        assert res.status_code == 201

        # Test in transactions search
        search_res = auth_client_john.get_transactions({"search": sqli_payload})
        assert search_res.status_code == 200

    @allure.story("XSS: Stored XSS Escaping in Cardholder Name")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.security
    def test_xss_escaping_in_cardholder(self, auth_client_john: FinPayApiClient):
        xss_payload = "<script>alert('xss')</script>"
        res = auth_client_john.create_card({
            "cardholder_name": xss_payload,
            "card_type": "VIRTUAL",
            "spending_limit": 500.0
        })
        assert res.status_code == 201
        data = res.json()
        assert data["cardholder_name"] == xss_payload.upper()
