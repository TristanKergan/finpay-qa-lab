# Risk Analysis & Mitigation Matrix: FinPay QA Lab

| Risk ID | Risk Description | Likelihood | Impact | Severity Score | Test Coverage & Architectural Mitigation |
|---|---|---|---|---|---|
| **R-01** | **Double Debiting via Concurrent Retries:** Network timeouts cause client to retry, resulting in multiple charges. | High | Critical | **CRITICAL** | Handled by unique idempotency keys in DB and atomic verification in `TransferService`. Verified by `test_transfer_idempotency_protection`. |
| **R-02** | **Negative Value Money Printing:** Attacker posts negative amount to inflate their balance. | Medium | Critical | **CRITICAL** | Enforced by Pydantic validator (`gt=0`) and service-level checks. Verified by `test_transfer_negative_amount`. |
| **R-03** | **IDOR on Sensitive Financial Records:** User guesses transaction UUID and reads private transaction counterparties. | High | High | **HIGH** | Strict owner authorization check (`user.id == sender_id or receiver_id`) returning HTTP 403. Tested in `test_unauthorized_transaction_access_idor`. |
| **R-04** | **Credential Stuffing & Brute Force:** Automated bots attempting thousands of passwords. | High | High | **HIGH** | Account locked automatically after 5 consecutive failed attempts. Tested in `test_account_lockout_after_failed_attempts`. |
| **R-05** | **Webhook Replay Attacks:** Adversary replays legitimate success webhook to trigger duplicate wallet credits. | Medium | Critical | **CRITICAL** | `ProcessedWebhook` tracking table enforcing unique event_id constraint. Tested in `test_duplicate_webhook_protection`. |
| **R-06** | **SQL Injection in Transaction Search:** Malicious search query crashes or exfiltrates database tables. | Medium | High | **HIGH** | SQLAlchemy parameterized statements and ORM query builders. Tested in `test_sqli_payload_resistance`. |
