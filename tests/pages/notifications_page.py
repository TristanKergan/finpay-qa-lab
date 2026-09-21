import allure
from playwright.sync_api import Page
from tests.pages.base_page import BasePage


class NotificationsPage(BasePage):
    ITEMS = '[data-testid="notification-item"]'
    MARK_READ_BTN = '[data-testid="btn-mark-read"]'
    MARK_ALL_READ_BTN = '[data-testid="btn-mark-all-read"]'

    def get_count(self) -> int:
        return self.page.locator(self.ITEMS).count()

    def mark_all_as_read(self):
        with allure.step("Mark all notifications as read"):
            self.click(self.MARK_ALL_READ_BTN)
