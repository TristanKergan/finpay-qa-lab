import pytest
import allure
from playwright.sync_api import Page
from tests.config.settings import test_settings
from tests.factories.user_factory import UserFactory
from tests.pages.login_page import LoginPage
from tests.pages.register_page import RegisterPage
from tests.pages.dashboard_page import DashboardPage


@allure.epic("UI Automation")
@allure.feature("Authentication Flows")
class TestUiAuth:

    @allure.story("Flow 1: User Registration (Positive)")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.ui
    def test_ui_registration_positive(self, browser_context: Page):
        page = browser_context
        login_page = LoginPage(page, test_settings.FRONTEND_URL)
        register_page = RegisterPage(page, test_settings.FRONTEND_URL)
        dashboard_page = DashboardPage(page, test_settings.FRONTEND_URL)

        login_page.open()
        login_page.go_to_register()

        userData = UserFactory.build()
        register_page.register(
            name=userData["full_name"],
            email=userData["email"],
            password=userData["password"],
            phone="+15550199"
        )

        # Should land on Dashboard with welcome greeting
        el = page.wait_for_selector(dashboard_page.USER_NAME, state="visible", timeout=10000)
        assert el is not None
        user_text = el.inner_text()
        assert userData["full_name"] in user_text

    @allure.story("Flow 2: User Login (Positive)")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.ui
    def test_ui_login_positive(self, browser_context: Page):
        page = browser_context
        login_page = LoginPage(page, test_settings.FRONTEND_URL)
        dashboard_page = DashboardPage(page, test_settings.FRONTEND_URL)

        login_page.open()
        login_page.login(test_settings.USER_JOHN_EMAIL, test_settings.USER_JOHN_PASSWORD)

        el = page.wait_for_selector(dashboard_page.USD_BALANCE, state="visible", timeout=10000)
        assert el is not None
        assert "$" in dashboard_page.get_usd_balance()

    @allure.story("Flow 2 (Negative): Invalid Password")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.ui
    def test_ui_login_negative_invalid_password(self, browser_context: Page):
        page = browser_context
        login_page = LoginPage(page, test_settings.FRONTEND_URL)

        login_page.open()
        login_page.login(test_settings.USER_JOHN_EMAIL, "WrongPassword999!")

        el = page.wait_for_selector(login_page.ERROR_ALERT, state="visible", timeout=10000)
        assert el is not None
        assert "invalid" in login_page.get_error_message().lower()

    @allure.story("Flow 2 (Negative): Locked Account Warning")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.ui
    def test_ui_login_negative_locked_account(self, browser_context: Page):
        page = browser_context
        login_page = LoginPage(page, test_settings.FRONTEND_URL)

        login_page.open()
        login_page.fill_demo_locked()
        login_page.click(login_page.LOGIN_BTN)

        el = page.wait_for_selector(login_page.ERROR_ALERT, state="visible", timeout=10000)
        assert el is not None
        assert "locked" in login_page.get_error_message().lower()

    @allure.story("Flow 3: Logout Flow")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.ui
    def test_ui_logout(self, browser_context: Page):
        page = browser_context
        login_page = LoginPage(page, test_settings.FRONTEND_URL)
        dashboard_page = DashboardPage(page, test_settings.FRONTEND_URL)

        login_page.open()
        login_page.login(test_settings.USER_JOHN_EMAIL, test_settings.USER_JOHN_PASSWORD)
        page.wait_for_selector(dashboard_page.USD_BALANCE, state="visible", timeout=10000)

        dashboard_page.logout()
        el = page.wait_for_selector(login_page.LOGIN_BTN, state="visible", timeout=10000)
        assert el is not None
