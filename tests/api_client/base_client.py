from typing import Any

import allure
import httpx

from tests.config.settings import test_settings
from tests.utils.allure_helpers import attach_json, attach_text


class BaseApiClient:
    def __init__(self, base_url: str | None = None):
        self.base_url = (base_url or test_settings.BASE_URL).rstrip("/")
        self.token: str | None = None

    def set_token(self, token: str):
        self.token = token

    def clear_token(self):
        self.token = None

    def _get_headers(self, custom_headers: dict[str, str] | None = None) -> dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        if custom_headers:
            headers.update(custom_headers)
        return headers

    def request(
        self,
        method: str,
        endpoint: str,
        json_data: Any | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> httpx.Response:
        url = f"{self.base_url}{endpoint}"
        req_headers = self._get_headers(headers)
        timeout_val = timeout or test_settings.REQUEST_TIMEOUT

        step_title = f"API Request: {method.upper()} {endpoint}"
        with allure.step(step_title):
            if json_data:
                attach_json(json_data, name="Request Body")
            if params:
                attach_json(params, name="Query Parameters")

            with httpx.Client(timeout=timeout_val) as client:
                response = client.request(
                    method=method,
                    url=url,
                    headers=req_headers,
                    json=json_data,
                    params=params,
                )

            # Log response in Allure
            try:
                res_body = response.json()
                attach_json(res_body, name=f"Response Body (Status {response.status_code})")
            except Exception:
                attach_text(response.text, name=f"Response Text (Status {response.status_code})")

            return response

    def get(self, endpoint: str, params: dict[str, Any] | None = None, headers: dict[str, str] | None = None) -> httpx.Response:
        return self.request("GET", endpoint, params=params, headers=headers)

    def post(self, endpoint: str, json_data: Any | None = None, params: dict[str, Any] | None = None, headers: dict[str, str] | None = None) -> httpx.Response:
        return self.request("POST", endpoint, json_data=json_data, params=params, headers=headers)

    def patch(self, endpoint: str, json_data: Any | None = None, headers: dict[str, str] | None = None) -> httpx.Response:
        return self.request("PATCH", endpoint, json_data=json_data, headers=headers)

    def delete(self, endpoint: str, headers: dict[str, str] | None = None) -> httpx.Response:
        return self.request("DELETE", endpoint, headers=headers)
