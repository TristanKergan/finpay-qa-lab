import allure
import pytest
from playwright.sync_api import Page

from tests.config.settings import test_settings
from tests.pages.dashboard_page import DashboardPage
from tests.pages.login_page import LoginPage
from tests.pages.transactions_page import TransactionsPage


@allure.epic("UI Automation")
@allure.feature("Transaction Ledger & Pagination Controls")
class TestUiTransactionsAndPagination:

    @allure.story("Flow 7: Transaction History Display")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.ui
    def test_ui_transaction_history_display(self, browser_context: Page):
        page = browser_context
        login_page = LoginPage(page, test_settings.FRONTEND_URL)
        dashboard_page = DashboardPage(page, test_settings.FRONTEND_URL)
        tx_page = TransactionsPage(page, test_settings.FRONTEND_URL)

        login_page.open()
        login_page.login(test_settings.USER_JOHN_EMAIL, test_settings.USER_JOHN_PASSWORD)

        # Navigate to transactions tab
        dashboard_page.click(dashboard_page.TAB_TRANSACTIONS)
        el = page.wait_for_selector(tx_page.TRANSACTION_ROWS, state="visible", timeout=10000)
        assert el is not None
        assert tx_page.get_row_count() > 0

    @allure.story("Flow 8: Transaction Pagination Navigation")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    def test_ui_transaction_pagination(self, browser_context: Page):
        page = browser_context
        login_page = LoginPage(page, test_settings.FRONTEND_URL)
        dashboard_page = DashboardPage(page, test_settings.FRONTEND_URL)
        tx_page = TransactionsPage(page, test_settings.FRONTEND_URL)

        login_page.open()
        login_page.login(test_settings.USER_JOHN_EMAIL, test_settings.USER_JOHN_PASSWORD)
        dashboard_page.click(dashboard_page.TAB_TRANSACTIONS)

        el = page.wait_for_selector(tx_page.CURRENT_PAGE_TEXT, state="visible", timeout=10000)
        assert el is not None
        cur_page = page.inner_text(tx_page.CURRENT_PAGE_TEXT)
        assert "Page 1" in cur_page
