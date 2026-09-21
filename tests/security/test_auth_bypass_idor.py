import allure
import pytest

from tests.api_client.finpay_api import FinPayApiClient
from tests.factories.user_factory import CardFactory


@allure.epic("Security Testing")
@allure.feature("Access Control & IDOR Protection")
class TestSecurityAccessControl:

    @allure.story("IDOR: Preventing Unauthorized Card Freeze")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.security
    def test_idor_card_freeze_prevention(
        self,
        auth_client_john: FinPayApiClient,
        auth_client_jane: FinPayApiClient
    ):
        # John creates a card
        card_res = auth_client_john.create_card(CardFactory.build())
        card_id = card_res.json()["id"]

        # Jane tries to freeze John's card
        idor_res = auth_client_jane.freeze_card(card_id)
        assert idor_res.status_code == 403, f"Expected 403, got {idor_res.status_code}"

    @allure.story("IDOR: Preventing Unauthorized Card Deletion")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.security
    def test_idor_card_delete_prevention(
        self,
        auth_client_john: FinPayApiClient,
        auth_client_jane: FinPayApiClient
    ):
        card_res = auth_client_john.create_card(CardFactory.build())
        card_id = card_res.json()["id"]

        idor_res = auth_client_jane.delete_card(card_id)
        assert idor_res.status_code == 403

    @allure.story("Authentication: Reject Tampered JWT Signature")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.security
    def test_reject_tampered_jwt(self, api_client: FinPayApiClient):
        tampered_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.invalid_tampered_signature_signature"
        api_client.set_token(tampered_token)

        res = api_client.get_wallet()
        assert res.status_code == 401
