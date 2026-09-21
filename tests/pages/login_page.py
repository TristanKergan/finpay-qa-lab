import allure
from playwright.sync_api import Page
from tests.pages.base_page import BasePage


class LoginPage(BasePage):
    EMAIL_INPUT = '[data-testid="input-email"]'
    PASSWORD_INPUT = '[data-testid="input-password"]'
    LOGIN_BTN = '[data-testid="btn-login"]'
    ERROR_ALERT = '[data-testid="login-error"]'
    REGISTER_LINK = '[data-testid="link-register"]'
    DEMO_JOHN_BTN = '[data-testid="btn-fill-john"]'
    DEMO_LOCKED_BTN = '[data-testid="btn-fill-locked"]'

    def open(self):
        self.navigate("/")

    def login(self, email: str, password: str):
        with allure.step(f"Log in as {email}"):
            self.fill(self.EMAIL_INPUT, email)
            self.fill(self.PASSWORD_INPUT, password)
            self.click(self.LOGIN_BTN)

    def fill_demo_john(self):
        with allure.step("Click quick-fill John Doe demo account"):
            self.click(self.DEMO_JOHN_BTN)

    def fill_demo_locked(self):
        with allure.step("Click quick-fill Locked User demo account"):
            self.click(self.DEMO_LOCKED_BTN)

    def get_error_message(self) -> str:
        return self.get_text(self.ERROR_ALERT)

    def go_to_register(self):
        with allure.step("Navigate to Register page"):
            self.click(self.REGISTER_LINK)
