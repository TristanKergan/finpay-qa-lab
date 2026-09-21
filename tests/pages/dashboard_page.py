import allure
from playwright.sync_api import Page
from tests.pages.base_page import BasePage


class DashboardPage(BasePage):
    USD_BALANCE = '[data-testid="wallet-balance-USD"]'
    EUR_BALANCE = '[data-testid="wallet-balance-EUR"]'
    UAH_BALANCE = '[data-testid="wallet-balance-UAH"]'
    TOTAL_BALANCE = '[data-testid="total-balance-usd"]'
    LOGOUT_BTN = '[data-testid="btn-logout"]'
    QUICK_TRANSFER_BTN = '[data-testid="btn-quick-transfer"]'
    QUICK_CARD_BTN = '[data-testid="btn-quick-card"]'
    NOTIFICATIONS_BTN = '[data-testid="btn-notifications"]'
    UNREAD_BADGE = '[data-testid="unread-badge"]'
    USER_NAME = '[data-testid="user-full-name"]'

    # Tabs
    TAB_DASHBOARD = '[data-testid="tab-dashboard"]'
    TAB_WALLET = '[data-testid="tab-wallet"]'
    TAB_TRANSFERS = '[data-testid="tab-transfers"]'
    TAB_TRANSACTIONS = '[data-testid="tab-transactions"]'
    TAB_CARDS = '[data-testid="tab-cards"]'
    TAB_NOTIFICATIONS = '[data-testid="tab-notifications"]'

    def get_usd_balance(self) -> str:
        return self.get_text(self.USD_BALANCE)

    def get_eur_balance(self) -> str:
        return self.get_text(self.EUR_BALANCE)

    def get_uah_balance(self) -> str:
        return self.get_text(self.UAH_BALANCE)

    def open_transfer_modal(self):
        with allure.step("Open transfer modal"):
            self.click(self.QUICK_TRANSFER_BTN)

    def open_card_modal(self):
        with allure.step("Open card modal"):
            self.click(self.QUICK_CARD_BTN)

    def logout(self):
        with allure.step("Logout user"):
            self.click(self.LOGOUT_BTN)
