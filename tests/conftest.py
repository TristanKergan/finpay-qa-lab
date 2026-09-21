import os
import subprocess
import time

import pytest
import requests
from playwright.sync_api import sync_playwright

from tests.api_client.finpay_api import FinPayApiClient
from tests.config.settings import test_settings
from tests.utils.allure_helpers import attach_screenshot, attach_text

_server_process = None
_frontend_process = None


@pytest.fixture(scope="session", autouse=True)
def ensure_servers():
    """Ensure both backend and frontend servers are running before tests execute."""
    global _server_process, _frontend_process

    # 1. Ensure Backend Server
    backend_up = False
    try:
        res = requests.get(f"{test_settings.BASE_URL}/health", timeout=1.0)
        if res.status_code == 200:
            backend_up = True
    except Exception:
        pass

    if not backend_up:
        print("\n🚀 Starting backend server on port 8000...")
        env = os.environ.copy()
        env["PYTHONPATH"] = "."
        backend_log = open("backend.log", "w")
        _server_process = subprocess.Popen(
            [".venv/bin/uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", "8000"],
            env=env,
            stdout=backend_log,
            stderr=backend_log
        )
        for _ in range(30):
            try:
                res = requests.get(f"{test_settings.BASE_URL}/health", timeout=1.0)
                if res.status_code == 200:
                    backend_up = True
                    break
            except Exception:
                time.sleep(0.3)

    # 2. Ensure Frontend Server
    frontend_up = False
    try:
        res = requests.get(test_settings.FRONTEND_URL, timeout=1.0)
        if res.status_code in [200, 304]:
            frontend_up = True
    except Exception:
        pass

    if not frontend_up:
        print("\n🌐 Starting frontend server on port 3000...")
        frontend_log = open("frontend.log", "w")
        _frontend_process = subprocess.Popen(
            ["npm", "run", "dev", "--prefix", "frontend", "--", "--port", "3000", "--host", "127.0.0.1"],
            stdout=frontend_log,
            stderr=frontend_log
        )
        for _ in range(30):
            try:
                res = requests.get(test_settings.FRONTEND_URL, timeout=1.0)
                if res.status_code in [200, 304]:
                    frontend_up = True
                    break
            except Exception:
                time.sleep(0.3)

    yield

    if _server_process:
        _server_process.terminate()
        _server_process.wait()
    if _frontend_process:
        _frontend_process.terminate()
        _frontend_process.wait()


@pytest.fixture(scope="function")
def api_client() -> FinPayApiClient:
    return FinPayApiClient()


@pytest.fixture(scope="function")
def auth_client_john(api_client: FinPayApiClient) -> FinPayApiClient:
    res = api_client.login(test_settings.USER_JOHN_EMAIL, test_settings.USER_JOHN_PASSWORD)
    assert res.status_code == 200, f"Failed to authenticate John Doe: {res.text}"
    return api_client


@pytest.fixture(scope="function")
def auth_client_jane() -> FinPayApiClient:
    client = FinPayApiClient()
    res = client.login(test_settings.USER_JANE_EMAIL, test_settings.USER_JANE_PASSWORD)
    assert res.status_code == 200, f"Failed to authenticate Jane Smith: {res.text}"
    return client


@pytest.fixture(scope="function")
def auth_client_qa() -> FinPayApiClient:
    client = FinPayApiClient()
    res = client.login(test_settings.USER_QA_EMAIL, test_settings.USER_QA_PASSWORD)
    assert res.status_code == 200, f"Failed to authenticate QA Tester: {res.text}"
    return client


@pytest.fixture(scope="function")
def browser_context():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=test_settings.PLAYWRIGHT_HEADLESS,
            slow_mo=test_settings.PLAYWRIGHT_SLOWMO
        )
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            base_url=test_settings.FRONTEND_URL
        )
        context.tracing.start(screenshots=True, snapshots=True, sources=True)
        page = context.new_page()

        yield page

        context.tracing.stop(path="allure-results/trace.zip")
        context.close()
        browser.close()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        if "browser_context" in item.fixturenames:
            try:
                page = item.funcargs.get("browser_context")
                if page:
                    screenshot = page.screenshot()
                    attach_screenshot(screenshot, name=f"Failure_{item.name}")
            except Exception as e:
                attach_text(f"Could not take screenshot: {e}", name="Screenshot Error")
