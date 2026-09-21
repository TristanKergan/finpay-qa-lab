import allure

from tests.pages.base_page import BasePage


class TransfersPage(BasePage):
    RECEIVER_INPUT = '[data-testid="input-receiver-email"]'
    CURRENCY_SELECT = '[data-testid="select-currency"]'
    AMOUNT_INPUT = '[data-testid="input-amount"]'
    DESCRIPTION_INPUT = '[data-testid="input-description"]'
    IDEMPOTENCY_INPUT = '[data-testid="input-idempotency-key"]'
    SUBMIT_BTN = '[data-testid="btn-submit-transfer"]'
    CLOSE_BTN = '[data-testid="btn-close-transfer"]'
    ALERT_ERROR = '[data-testid="transfer-alert-error"]'
    ALERT_SUCCESS = '[data-testid="transfer-alert-success"]'

    def send_money(self, receiver_email: str, currency: str, amount: float, description: str = "", idempotency_key: str = None):
        with allure.step(f"Perform money transfer of {amount} {currency} to {receiver_email}"):
            self.fill(self.RECEIVER_INPUT, receiver_email)
            self.select_option(self.CURRENCY_SELECT, currency)
            self.fill(self.AMOUNT_INPUT, str(amount))
            if description:
                self.fill(self.DESCRIPTION_INPUT, description)
            if idempotency_key:
                self.fill(self.IDEMPOTENCY_INPUT, idempotency_key)
            self.click(self.SUBMIT_BTN)

    def get_error_message(self) -> str:
        return self.get_text(self.ALERT_ERROR)

    def get_success_message(self) -> str:
        return self.get_text(self.ALERT_SUCCESS)
