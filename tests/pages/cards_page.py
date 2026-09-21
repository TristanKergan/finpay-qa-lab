import allure
from playwright.sync_api import Page
from tests.pages.base_page import BasePage


class CardsPage(BasePage):
    NEW_CARD_BTN = '[data-testid="btn-create-card"]'
    CARDHOLDER_INPUT = '[data-testid="input-cardholder-name"]'
    CARD_TYPE_SELECT = '[data-testid="select-card-type"]'
    LIMIT_INPUT = '[data-testid="input-spending-limit"]'
    SUBMIT_CARD_BTN = '[data-testid="btn-submit-card"]'
    
    CARD_ITEMS = '[data-testid="card-item"]'
    FREEZE_BTN = '[data-testid="btn-freeze-card"]'
    UNFREEZE_BTN = '[data-testid="btn-unfreeze-card"]'
    DELETE_BTN = '[data-testid="btn-delete-card"]'
    CARD_STATUS = '[data-testid="card-status"]'

    def create_card(self, cardholder: str, card_type: str = "VIRTUAL", limit: float = 1000):
        with allure.step(f"Create new virtual card for {cardholder}"):
            self.click(self.NEW_CARD_BTN)
            self.fill(self.CARDHOLDER_INPUT, cardholder)
            self.select_option(self.CARD_TYPE_SELECT, card_type)
            self.fill(self.LIMIT_INPUT, str(limit))
            self.click(self.SUBMIT_CARD_BTN)

    def get_cards_count(self) -> int:
        return self.page.locator(self.CARD_ITEMS).count()

    def freeze_first_card(self):
        with allure.step("Freeze first card"):
            self.page.locator(self.FREEZE_BTN).first.click()

    def unfreeze_first_card(self):
        with allure.step("Unfreeze first card"):
            self.page.locator(self.UNFREEZE_BTN).first.click()
