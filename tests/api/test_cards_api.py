import allure
import pytest

from tests.api_client.finpay_api import FinPayApiClient
from tests.factories.user_factory import CardFactory
from tests.schemas.api_schemas import CardSchema


@allure.epic("Virtual Cards")
@allure.feature("Card Lifecycle Management")
class TestCardsApi:

    @allure.story("Positive: Create Virtual Card")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.api
    def test_create_card(self, auth_client_john: FinPayApiClient):
        payload = CardFactory.build(cardholder_name="JOHN DOE", spending_limit=1500.0)
        res = auth_client_john.create_card(payload)
        assert res.status_code == 201
        data = res.json()
        CardSchema.model_validate(data)
        assert data["card_number_masked"].startswith("**** **** **** ")
        assert data["status"] == "ACTIVE"
        assert data["spending_limit"] == 1500.0

    @allure.story("Positive: Freeze and Unfreeze Virtual Card")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.api
    def test_freeze_and_unfreeze_card(self, auth_client_john: FinPayApiClient):
        # Create
        c_res = auth_client_john.create_card(CardFactory.build())
        card_id = c_res.json()["id"]

        # Freeze
        fr_res = auth_client_john.freeze_card(card_id)
        assert fr_res.status_code == 200
        assert fr_res.json()["status"] == "FROZEN"

        # Freeze again -> should return 400
        fr2_res = auth_client_john.freeze_card(card_id)
        assert fr2_res.status_code == 400

        # Unfreeze
        un_res = auth_client_john.unfreeze_card(card_id)
        assert un_res.status_code == 200
        assert un_res.json()["status"] == "ACTIVE"

    @allure.story("Positive: Delete Virtual Card")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    def test_delete_card(self, auth_client_john: FinPayApiClient):
        c_res = auth_client_john.create_card(CardFactory.build())
        card_id = c_res.json()["id"]

        del_res = auth_client_john.delete_card(card_id)
        assert del_res.status_code == 204

        # Cannot freeze deleted card
        fr_res = auth_client_john.freeze_card(card_id)
        assert fr_res.status_code == 404
