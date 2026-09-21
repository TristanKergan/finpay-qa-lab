import allure
from playwright.sync_api import Page, Locator
from tests.utils.allure_helpers import attach_screenshot


class BasePage:
    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")

    def navigate(self, path: str = ""):
        url = f"{self.base_url}{path}"
        with allure.step(f"Navigate to {url}"):
            self.page.goto(url, wait_until="networkidle")

    def click(self, selector: str):
        with allure.step(f"Click element: {selector}"):
            self.page.wait_for_selector(selector, state="visible", timeout=10000)
            self.page.click(selector)

    def fill(self, selector: str, text: str):
        with allure.step(f"Fill {selector} with '{text}'"):
            self.page.wait_for_selector(selector, state="visible", timeout=10000)
            self.page.fill(selector, text)

    def select_option(self, selector: str, value: str):
        with allure.step(f"Select option '{value}' in {selector}"):
            self.page.wait_for_selector(selector, state="visible", timeout=10000)
            self.page.select_option(selector, value)

    def get_text(self, selector: str) -> str:
        self.page.wait_for_selector(selector, state="visible", timeout=10000)
        return self.page.inner_text(selector).strip()

    def is_visible(self, selector: str, timeout: float = 3000) -> bool:
        try:
            self.page.wait_for_selector(selector, state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    def take_screenshot(self, name: str = "Page Screenshot"):
        screenshot = self.page.screenshot()
        attach_screenshot(screenshot, name=name)
