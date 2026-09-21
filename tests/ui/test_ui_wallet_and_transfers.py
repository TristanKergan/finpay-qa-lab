import pytest
import allure
from playwright.sync_api import Page
from tests.config.settings import test_settings
from tests.pages.dashboard_page import DashboardPage
from tests.pages.login_page import LoginPage
from tests.pages.transfers_page import TransfersPage


@allure.epic("UI Automation")
@allure.feature("Wallet Balances & Money Transfer Flows")
class TestUiWalletAndTransfers:

    @allure.story("Flow 4: Wallet Balance Display (Multi-Currency)")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.ui
    def test_ui_wallet_balances_display(self, browser_context: Page):
        page = browser_context
        login_page = LoginPage(page, test_settings.FRONTEND_URL)
        dashboard_page = DashboardPage(page, test_settings.FRONTEND_URL)

        login_page.open()
        login_page.login(test_settings.USER_JOHN_EMAIL, test_settings.USER_JOHN_PASSWORD)

        assert page.wait_for_selector(dashboard_page.USD_BALANCE, state="visible", timeout=10000)
        assert page.wait_for_selector(dashboard_page.EUR_BALANCE, state="visible", timeout=10000)
        assert page.wait_for_selector(dashboard_page.UAH_BALANCE, state="visible", timeout=10000)
        assert page.wait_for_selector(dashboard_page.TOTAL_BALANCE, state="visible", timeout=10000)

    @allure.story("Flow 5: Money Transfer (Positive)")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.ui
    def test_ui_transfer_money_success(self, browser_context: Page):
        page = browser_context
        login_page = LoginPage(page, test_settings.FRONTEND_URL)
        dashboard_page = DashboardPage(page, test_settings.FRONTEND_URL)
        transfers_page = TransfersPage(page, test_settings.FRONTEND_URL)

        login_page.open()
        login_page.login(test_settings.USER_JOHN_EMAIL, test_settings.USER_JOHN_PASSWORD)
        page.wait_for_selector(dashboard_page.USD_BALANCE, state="visible", timeout=10000)
        dashboard_page.open_transfer_modal()

        transfers_page.send_money(
            receiver_email=test_settings.USER_JANE_EMAIL,
            currency="USD",
            amount=25.0,
            description="Playwright Automated UI Transfer"
        )

        el = page.wait_for_selector(transfers_page.ALERT_SUCCESS, state="visible", timeout=10000)
        assert el is not None
        assert "successfully" in transfers_page.get_success_message().lower()

    @allure.story("Flow 6: Insufficient Funds Alert")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.ui
    def test_ui_transfer_insufficient_funds(self, browser_context: Page):
        page = browser_context
        login_page = LoginPage(page, test_settings.FRONTEND_URL)
        dashboard_page = DashboardPage(page, test_settings.FRONTEND_URL)
        transfers_page = TransfersPage(page, test_settings.FRONTEND_URL)

        login_page.open()
        login_page.login(test_settings.USER_JOHN_EMAIL, test_settings.USER_JOHN_PASSWORD)
        page.wait_for_selector(dashboard_page.USD_BALANCE, state="visible", timeout=10000)
        dashboard_page.open_transfer_modal()

        transfers_page.send_money(
            receiver_email=test_settings.USER_JANE_EMAIL,
            currency="USD",
            amount=9999999.0
        )

        el = page.wait_for_selector(transfers_page.ALERT_ERROR, state="visible", timeout=10000)
        assert el is not None
        assert "insufficient" in transfers_page.get_error_message().lower()
