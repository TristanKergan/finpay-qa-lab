import json

import allure


def attach_json(data: dict, name: str = "JSON Payload"):
    allure.attach(
        json.dumps(data, indent=2, default=str),
        name=name,
        attachment_type=allure.attachment_type.JSON
    )


def attach_text(text: str, name: str = "Log Text"):
    allure.attach(
        text,
        name=name,
        attachment_type=allure.attachment_type.TEXT
    )


def attach_screenshot(screenshot_bytes: bytes, name: str = "Failure Screenshot"):
    allure.attach(
        screenshot_bytes,
        name=name,
        attachment_type=allure.attachment_type.PNG
    )
