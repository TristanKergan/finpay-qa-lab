import allure
import pytest
from playwright.sync_api import Page

from tests.config.settings import test_settings
from tests.pages.cards_page import CardsPage
from tests.pages.dashboard_page import DashboardPage
from tests.pages.login_page import LoginPage
from tests.pages.notifications_page import NotificationsPage


@allure.epic("UI Automation")
@allure.feature("Virtual Cards & Notification Center")
class TestUiCardsAndNotifications:

    @allure.story("Flow 9: Virtual Card Creation")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.ui
    def test_ui_card_creation(self, browser_context: Page):
        page = browser_context
        login_page = LoginPage(page, test_settings.FRONTEND_URL)
        dashboard_page = DashboardPage(page, test_settings.FRONTEND_URL)
        cards_page = CardsPage(page, test_settings.FRONTEND_URL)

        login_page.open()
        login_page.login(test_settings.USER_QA_EMAIL, test_settings.USER_QA_PASSWORD)
        dashboard_page.click(dashboard_page.TAB_CARDS)

        page.wait_for_selector(cards_page.NEW_CARD_BTN, state="visible", timeout=10000)
        initial_count = cards_page.get_cards_count()
        cards_page.create_card(cardholder="QA ROBOT", card_type="VIRTUAL", limit=2000)

        page.wait_for_timeout(1000)
        assert cards_page.get_cards_count() >= initial_count + 1

    @allure.story("Flow 10: Freeze & Unfreeze Card")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.ui
    def test_ui_freeze_card(self, browser_context: Page):
        page = browser_context
        login_page = LoginPage(page, test_settings.FRONTEND_URL)
        dashboard_page = DashboardPage(page, test_settings.FRONTEND_URL)
        cards_page = CardsPage(page, test_settings.FRONTEND_URL)

        login_page.open()
        login_page.login(test_settings.USER_QA_EMAIL, test_settings.USER_QA_PASSWORD)
        dashboard_page.click(dashboard_page.TAB_CARDS)

        page.wait_for_selector(cards_page.NEW_CARD_BTN, state="visible", timeout=10000)
        if not page.is_visible(cards_page.FREEZE_BTN):
            cards_page.create_card(cardholder="QA FREEZE", card_type="DEBIT", limit=500)
            page.wait_for_timeout(1000)

        cards_page.freeze_first_card()
        el = page.wait_for_selector(cards_page.UNFREEZE_BTN, state="visible", timeout=10000)
        assert el is not None

    @allure.story("Flow 11: Notification Center & Mark All Read")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    def test_ui_notifications(self, browser_context: Page):
        page = browser_context
        login_page = LoginPage(page, test_settings.FRONTEND_URL)
        dashboard_page = DashboardPage(page, test_settings.FRONTEND_URL)
        notes_page = NotificationsPage(page, test_settings.FRONTEND_URL)

        login_page.open()
        login_page.login(test_settings.USER_JOHN_EMAIL, test_settings.USER_JOHN_PASSWORD)
        dashboard_page.click(dashboard_page.TAB_NOTIFICATIONS)

        assert page.wait_for_selector(notes_page.ITEMS, state="visible", timeout=10000)
        notes_page.mark_all_as_read()
        page.wait_for_timeout(500)
