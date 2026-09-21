import concurrent.futures
import uuid

import allure
import pytest

from tests.api_client.finpay_api import FinPayApiClient
from tests.factories.user_factory import UserFactory


@allure.epic("Concurrency & Race Condition Prevention")
@allure.feature("ACID Transaction Isolation & Concurrent Idempotency")
class TestConcurrentTransfers:

    @allure.story("Concurrent Transfers: Identical Idempotency Key")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.integration
    def test_concurrent_transfers_same_idempotency_key(self):
        """
        Verify that multiple concurrent transfer requests with the exact same
        idempotency_key result in:
        1. Exactly one transaction created in the database.
        2. Sender balance decremented exactly once.
        3. Receiver balance incremented exactly once.
        4. All concurrent callers receive a consistent response (status 200/201, same transaction_id).
        """
        # Create fresh sender and receiver
        client_sender = FinPayApiClient()
        client_receiver = FinPayApiClient()

        sender_data = UserFactory.build()
        receiver_data = UserFactory.build()

        client_sender.register(sender_data)
        client_sender.login(sender_data["email"], sender_data["password"])

        client_receiver.register(receiver_data)
        client_receiver.login(receiver_data["email"], receiver_data["password"])

        sender_w_before = client_sender.get_wallet().json()["wallets"]
        receiver_w_before = client_receiver.get_wallet().json()["wallets"]

        sender_usd_before = next(w["balance"] for w in sender_w_before if w["currency"] == "USD")
        receiver_usd_before = next(w["balance"] for w in receiver_w_before if w["currency"] == "USD")

        transfer_amount = 75.0
        shared_idempotency_key = f"concurrent_idem_{uuid.uuid4().hex}"

        payload = {
            "receiver_email": receiver_data["email"],
            "currency": "USD",
            "amount": transfer_amount,
            "description": "Simultaneous concurrent transfer test",
            "idempotency_key": shared_idempotency_key
        }

        # Issue 5 simultaneous requests from concurrent worker threads
        num_workers = 5
        responses = []

        def send_transfer():
            c = FinPayApiClient()
            c.login(sender_data["email"], sender_data["password"])
            return c.create_transfer(payload)

        with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(send_transfer) for _ in range(num_workers)]
            for future in concurrent.futures.as_completed(futures):
                responses.append(future.result())

        # 1. Verify all requests completed with successful 200/201 (consistent idempotent result)
        status_codes = [r.status_code for r in responses]
        if any(code == 500 for code in status_codes):
            print("500 ERRORS:", [r.text for r in responses if r.status_code == 500])
        assert all(code in [200, 201] for code in status_codes), f"Unexpected status codes: {status_codes}"

        # 2. Verify all callers received the identical transaction_id
        txn_ids = {r.json()["transaction_id"] for r in responses}
        assert len(txn_ids) == 1, f"Expected exactly 1 unique transaction_id, got: {txn_ids}"
        single_txn_id = txn_ids.pop()
        assert len(single_txn_id) > 0

        # 3. Verify sender balance decremented exactly once
        sender_w_after = client_sender.get_wallet().json()["wallets"]
        sender_usd_after = next(w["balance"] for w in sender_w_after if w["currency"] == "USD")
        expected_sender_balance = round(sender_usd_before - transfer_amount, 2)
        assert sender_usd_after == expected_sender_balance, (
            f"Sender balance mismatch! Before: {sender_usd_before}, After: {sender_usd_after}, Expected: {expected_sender_balance}"
        )

        # 4. Verify receiver balance incremented exactly once
        receiver_w_after = client_receiver.get_wallet().json()["wallets"]
        receiver_usd_after = next(w["balance"] for w in receiver_w_after if w["currency"] == "USD")
        expected_receiver_balance = round(receiver_usd_before + transfer_amount, 2)
        assert receiver_usd_after == expected_receiver_balance, (
            f"Receiver balance mismatch! Before: {receiver_usd_before}, After: {receiver_usd_after}, Expected: {expected_receiver_balance}"
        )

    @allure.story("Concurrent Overdraft Protection: Different Idempotency Keys")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.integration
    def test_concurrent_transfers_overdraft_race_condition(self):
        """
        Verify that when two concurrent transfers compete for funds and total amount
        exceeds available balance, exactly one succeeds and the other fails with 400,
        preventing account overdraft.
        """
        client_sender = FinPayApiClient()
        client_receiver = FinPayApiClient()

        sender_data = UserFactory.build()
        receiver_data = UserFactory.build()

        client_sender.register(sender_data)
        client_sender.login(sender_data["email"], sender_data["password"])

        client_receiver.register(receiver_data)
        client_receiver.login(receiver_data["email"], receiver_data["password"])

        # Default starting USD balance is 1000.0
        # Send two simultaneous transfers of 600.0 USD each (Total = 1200.0 > 1000.0)
        num_transfers = 2
        amount = 600.0

        def send_competing_transfer():
            c = FinPayApiClient()
            c.login(sender_data["email"], sender_data["password"])
            return c.create_transfer({
                "receiver_email": receiver_data["email"],
                "currency": "USD",
                "amount": amount,
                "idempotency_key": f"competing_{uuid.uuid4().hex}"
            })

        with concurrent.futures.ThreadPoolExecutor(max_workers=num_transfers) as executor:
            futures = [executor.submit(send_competing_transfer) for _ in range(num_transfers)]
            responses = [f.result() for f in concurrent.futures.as_completed(futures)]

        status_codes = [r.status_code for r in responses]
        # Exactly one must succeed (201) and one must be rejected (400 Insufficient funds)
        assert 201 in status_codes, "At least one transfer should succeed"
        assert 400 in status_codes, "Overdraft transfer should be rejected with 400"

        # Verify sender balance did not overdraft below zero
        sender_w_after = client_sender.get_wallet().json()["wallets"]
        sender_usd_after = next(w["balance"] for w in sender_w_after if w["currency"] == "USD")
        assert sender_usd_after == 400.0, f"Expected 400.0 balance remaining, got {sender_usd_after}"
