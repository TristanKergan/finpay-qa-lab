import allure
import pytest

from tests.api_client.finpay_api import FinPayApiClient
from tests.factories.user_factory import UserFactory


@allure.epic("Integration & End-to-End Workflows")
@allure.feature("Full Transfer Lifecycle with Notifications & Auditing")
class TestTransferLifecycle:

    @allure.story("E2E: Complete Multi-User Transfer Workflow")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.integration
    def test_complete_transfer_lifecycle(self, api_client: FinPayApiClient):
        # 1. Register Alice & Bob
        alice_data = UserFactory.build()
        bob_data = UserFactory.build()

        client_alice = FinPayApiClient()
        client_bob = FinPayApiClient()

        client_alice.register(alice_data)
        client_alice.login(alice_data["email"], alice_data["password"])

        client_bob.register(bob_data)
        client_bob.login(bob_data["email"], bob_data["password"])

        # 2. Check initial balances
        alice_w_before = client_alice.get_wallet().json()["wallets"]
        bob_w_before = client_bob.get_wallet().json()["wallets"]

        alice_usd_before = next(w["balance"] for w in alice_w_before if w["currency"] == "USD")
        bob_usd_before = next(w["balance"] for w in bob_w_before if w["currency"] == "USD")

        # 3. Alice transfers 150.0 USD to Bob
        transfer_res = client_alice.create_transfer({
            "receiver_email": bob_data["email"],
            "currency": "USD",
            "amount": 150.0,
            "description": "Lifecycle test payment"
        })
        assert transfer_res.status_code == 201
        txn_id = transfer_res.json()["transaction_id"]

        # 4. Check balances after transfer
        alice_w_after = client_alice.get_wallet().json()["wallets"]
        bob_w_after = client_bob.get_wallet().json()["wallets"]

        alice_usd_after = next(w["balance"] for w in alice_w_after if w["currency"] == "USD")
        bob_usd_after = next(w["balance"] for w in bob_w_after if w["currency"] == "USD")

        assert alice_usd_after == round(alice_usd_before - 150.0, 2)
        assert bob_usd_after == round(bob_usd_before + 150.0, 2)

        # 5. Check Alice's notifications (sent)
        alice_notes = client_alice.get_notifications().json()["items"]
        assert any("Money Sent" in n["title"] or "TRANSFER_SUCCESS" in n["type"] for n in alice_notes)

        # 6. Check Bob's notifications (received)
        bob_notes = client_bob.get_notifications().json()["items"]
        assert any("Money Received" in n["title"] or "TRANSFER_INCOMING" in n["type"] for n in bob_notes)

        # 7. Check Alice's transaction list
        alice_txns = client_alice.get_transactions().json()["items"]
        assert any(t["id"] == txn_id for t in alice_txns)

        # 8. Check Bob's transaction list
        bob_txns = client_bob.get_transactions().json()["items"]
        assert any(t["id"] == txn_id for t in bob_txns)
