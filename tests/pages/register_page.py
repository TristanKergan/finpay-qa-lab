import allure
from playwright.sync_api import Page
from tests.pages.base_page import BasePage


class RegisterPage(BasePage):
    NAME_INPUT = '[data-testid="input-name"]'
    EMAIL_INPUT = '[data-testid="input-email"]'
    PASSWORD_INPUT = '[data-testid="input-password"]'
    PHONE_INPUT = '[data-testid="input-phone"]'
    REGISTER_BTN = '[data-testid="btn-register"]'
    ERROR_ALERT = '[data-testid="register-error"]'
    LOGIN_LINK = '[data-testid="link-login"]'

    def register(self, name: str, email: str, password: str, phone: str = ""):
        with allure.step(f"Register new account for {email}"):
            self.fill(self.NAME_INPUT, name)
            self.fill(self.EMAIL_INPUT, email)
            self.fill(self.PASSWORD_INPUT, password)
            if phone:
                self.fill(self.PHONE_INPUT, phone)
            self.click(self.REGISTER_BTN)

    def get_error_message(self) -> str:
        return self.get_text(self.ERROR_ALERT)
