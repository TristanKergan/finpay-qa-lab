from typing import Any, Dict, Optional
import httpx
from tests.api_client.base_client import BaseApiClient


class FinPayApiClient(BaseApiClient):
    """Fluent high-level API Client for FinPay QA Lab."""

    # Auth
    def register(self, payload: dict) -> httpx.Response:
        return self.post("/api/v1/auth/register", json_data=payload)

    def login(self, email: str, password: str) -> httpx.Response:
        res = self.post("/api/v1/auth/login", json_data={"email": email, "password": password})
        if res.status_code == 200:
            self.set_token(res.json().get("access_token"))
        return res

    def refresh(self, refresh_token: str) -> httpx.Response:
        return self.post("/api/v1/auth/refresh", json_data={"refresh_token": refresh_token})

    def logout(self, refresh_token: str) -> httpx.Response:
        return self.post("/api/v1/auth/logout", json_data={"refresh_token": refresh_token})

    def change_password(self, old_pwd: str, new_pwd: str) -> httpx.Response:
        return self.post("/api/v1/auth/password/change", json_data={"old_password": old_pwd, "new_password": new_pwd})

    def reset_password(self, email: str, new_pwd: str) -> httpx.Response:
        return self.post("/api/v1/auth/password/reset", json_data={"email": email, "new_password": new_pwd})

    # Users
    def get_me(self) -> httpx.Response:
        return self.get("/api/v1/users/me")

    def update_me(self, payload: dict) -> httpx.Response:
        return self.patch("/api/v1/users/me", json_data=payload)

    def list_users(self) -> httpx.Response:
        return self.get("/api/v1/users")

    # Wallet
    def get_wallet(self) -> httpx.Response:
        return self.get("/api/v1/wallet")

    # Transfers
    def create_transfer(self, payload: dict) -> httpx.Response:
        return self.post("/api/v1/transfers", json_data=payload)

    def get_transfer(self, transfer_id: str) -> httpx.Response:
        return self.get(f"/api/v1/transfers/{transfer_id}")

    # Transactions
    def get_transactions(self, params: Optional[dict] = None) -> httpx.Response:
        return self.get("/api/v1/transactions", params=params)

    def get_transaction(self, txn_id: str) -> httpx.Response:
        return self.get(f"/api/v1/transactions/{txn_id}")

    # Cards
    def create_card(self, payload: dict) -> httpx.Response:
        return self.post("/api/v1/cards", json_data=payload)

    def list_cards(self) -> httpx.Response:
        return self.get("/api/v1/cards")

    def freeze_card(self, card_id: str) -> httpx.Response:
        return self.patch(f"/api/v1/cards/{card_id}/freeze")

    def unfreeze_card(self, card_id: str) -> httpx.Response:
        return self.patch(f"/api/v1/cards/{card_id}/unfreeze")

    def delete_card(self, card_id: str) -> httpx.Response:
        return self.delete(f"/api/v1/cards/{card_id}")

    # Notifications
    def get_notifications(self) -> httpx.Response:
        return self.get("/api/v1/notifications")

    def mark_notification_read(self, note_id: str) -> httpx.Response:
        return self.patch(f"/api/v1/notifications/{note_id}/read")

    def mark_all_notifications_read(self) -> httpx.Response:
        return self.post("/api/v1/notifications/read-all")

    # Webhooks & Mock Provider
    def post_webhook(self, payload: dict) -> httpx.Response:
        return self.post("/api/v1/webhooks/payment", json_data=payload)

    def mock_process_payment(self, payload: dict) -> httpx.Response:
        return self.post("/mock/payment/process", json_data=payload)

    # QA Testing Hooks
    def set_debug_bugs(self, payload: dict) -> httpx.Response:
        return self.post("/api/debug/bugs", json_data=payload)
