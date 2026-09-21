import allure
from playwright.sync_api import Page
from tests.pages.base_page import BasePage


class TransactionsPage(BasePage):
    SEARCH_INPUT = '[data-testid="input-search-txns"]'
    FILTER_STATUS = '[data-testid="filter-status"]'
    FILTER_CURRENCY = '[data-testid="filter-currency"]'
    TRANSACTION_ROWS = '[data-testid="transaction-row"]'
    PREV_PAGE_BTN = '[data-testid="btn-prev-page"]'
    NEXT_PAGE_BTN = '[data-testid="btn-next-page"]'
    CURRENT_PAGE_TEXT = '[data-testid="text-current-page"]'

    def search(self, text: str):
        with allure.step(f"Search transactions for '{text}'"):
            self.fill(self.SEARCH_INPUT, text)

    def filter_status(self, status: str):
        with allure.step(f"Filter transactions by status '{status}'"):
            self.select_option(self.FILTER_STATUS, status)

    def get_row_count(self) -> int:
        return self.page.locator(self.TRANSACTION_ROWS).count()

    def next_page(self):
        with allure.step("Navigate to next transactions page"):
            self.click(self.NEXT_PAGE_BTN)

    def prev_page(self):
        with allure.step("Navigate to previous transactions page"):
            self.click(self.PREV_PAGE_BTN)
