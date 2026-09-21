import allure
import pytest

from tests.api_client.finpay_api import FinPayApiClient
from tests.factories.user_factory import UserFactory
from tests.schemas.api_schemas import TokenSchema, UserSchema


@allure.epic("Authentication & Authorization")
@allure.feature("User Registration & Login")
class TestAuthApi:

    @allure.story("Positive: Successful User Registration")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.api
    def test_register_success(self, api_client: FinPayApiClient):
        payload = UserFactory.build()
        res = api_client.register(payload)
        assert res.status_code == 201, f"Expected 201, got {res.status_code}: {res.text}"
        data = res.json()
        UserSchema.model_validate(data)
        assert data["email"] == payload["email"].lower()
        assert data["full_name"] == payload["full_name"]
        assert data["status"] == "ACTIVE"

    @allure.story("Negative: Register Duplicate Email")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    def test_register_duplicate_email(self, api_client: FinPayApiClient):
        payload = UserFactory.build()
        res1 = api_client.register(payload)
        assert res1.status_code == 201

        res2 = api_client.register(payload)
        assert res2.status_code == 400
        assert "already exists" in res2.json().get("detail", "").lower()

    @allure.story("Negative: Register With Short Password")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    def test_register_short_password_validation(self, api_client: FinPayApiClient):
        payload = UserFactory.build(password="123")
        res = api_client.register(payload)
        assert res.status_code == 422, f"Expected 422 validation error, got {res.status_code}"

    @allure.story("Positive: Successful User Login")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.api
    def test_login_success(self, api_client: FinPayApiClient):
        payload = UserFactory.build()
        api_client.register(payload)

        res = api_client.login(payload["email"], payload["password"])
        assert res.status_code == 200
        data = res.json()
        TokenSchema.model_validate(data)
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["email"] == payload["email"].lower()

    @allure.story("Negative: Invalid Password Login")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.api
    def test_login_invalid_password(self, api_client: FinPayApiClient):
        payload = UserFactory.build()
        api_client.register(payload)

        res = api_client.login(payload["email"], "WrongPassword999!")
        assert res.status_code == 401
        assert "invalid" in res.json().get("detail", "").lower()

    @allure.story("Security: Account Lockout after Consecutive Failed Logins")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.api
    def test_account_lockout_after_failed_attempts(self, api_client: FinPayApiClient):
        payload = UserFactory.build()
        api_client.register(payload)

        # Attempt 5 wrong passwords
        for i in range(5):
            res = api_client.login(payload["email"], f"WrongPassword_{i}!")
            if i < 4:
                assert res.status_code == 401
            else:
                assert res.status_code == 403
                assert "locked" in res.json().get("detail", "").lower()

        # 6th attempt should be immediately blocked
        blocked_res = api_client.login(payload["email"], payload["password"])
        assert blocked_res.status_code == 403

    @allure.story("Positive: Refresh Token Rotation")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.api
    def test_refresh_token_rotation(self, api_client: FinPayApiClient):
        payload = UserFactory.build()
        api_client.register(payload)
        login_res = api_client.login(payload["email"], payload["password"])
        refresh_token = login_res.json()["refresh_token"]

        ref_res = api_client.refresh(refresh_token)
        assert ref_res.status_code == 200
        new_data = ref_res.json()
        TokenSchema.model_validate(new_data)
        assert new_data["refresh_token"] != refresh_token

        # Old refresh token should now be invalid
        old_ref_res = api_client.refresh(refresh_token)
        assert old_ref_res.status_code == 401

    @allure.story("Positive: User Logout")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    def test_logout(self, api_client: FinPayApiClient):
        payload = UserFactory.build()
        api_client.register(payload)
        login_res = api_client.login(payload["email"], payload["password"])
        refresh_token = login_res.json()["refresh_token"]

        logout_res = api_client.logout(refresh_token)
        assert logout_res.status_code == 204

        # Token should be revoked
        ref_res = api_client.refresh(refresh_token)
        assert ref_res.status_code == 401
