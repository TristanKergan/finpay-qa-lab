# Comprehensive Bug Reports: FinPay QA Lab (BUG_MODE)

This repository contains an intentional, production-grade defect simulation engine toggled via `BUG_MODE=true` (or fine-grained flags). The 10 realistic defects below mirror actual high-severity bugs found in real-world fintech systems.

---

### BUG-001: Idempotency Key Bypass Causes Double Debit
- **ID:** BUG-001
- **Title:** Replaying a transfer request with an identical idempotency key debits the sender twice instead of returning cached result.
- **Component:** `TransferService` (`transfer_service.py`)
- **Severity:** Blocker (S1)
- **Priority:** High (P1)
- **Environment:** `BUG_MODE=true` or `BUG_001_DUPLICATE_TRANSFER=true`
- **Preconditions:** Sender has sufficient balance.
- **Steps to Reproduce:**
  1. Send `POST /api/v1/transfers` with `amount=10.0`, `currency="USD"`, `idempotency_key="idem_12345"`.
  2. Send exact same request again with identical `idempotency_key="idem_12345"`.
- **Expected Result:** System recognizes duplicate key, skips second transaction, and returns HTTP 200/201 with original transaction data. Balance debited by $10.00.
- **Actual Result:** Second transaction is executed and creates a second debit, deducting $20.00 total.
- **Evidence:** Automated reproduction in `tests/integration/test_bug_mode_matrix.py::test_bug_001_duplicate_transfer_detection`.
- **Status:** Documented / Reproducible in BUG_MODE.

---

### BUG-002: Duplicate Webhook Delivery Double-Credits Receiver
- **ID:** BUG-002
- **Title:** External provider webhook deduplication fails, crediting wallet multiple times on replayed events.
- **Component:** `WebhookService` (`webhook_service.py`)
- **Severity:** Blocker (S1)
- **Priority:** High (P1)
- **Environment:** `BUG_MODE=true` or `BUG_002_DUPLICATE_WEBHOOK=true`
- **Steps to Reproduce:**
  1. Post payment webhook with `event_id="evt_001"`, `status="SUCCESS"`.
  2. Replay payment webhook with identical `event_id="evt_001"`.
- **Expected Result:** Second webhook returns `ALREADY_PROCESSED`. Ledger balance remains unchanged.
- **Actual Result:** Webhook is processed again, creating duplicate balance credits.
- **Evidence:** Verified in `test_bug_002_duplicate_webhook`.
- **Status:** Documented / Reproducible in BUG_MODE.

---

### BUG-003: Expired JWT Allows Access to Transaction History
- **ID:** BUG-003
- **Title:** Transaction endpoint skips JWT `exp` validation, allowing stale tokens to read financial records.
- **Component:** `Security` / `API Dependencies` (`deps.py`)
- **Severity:** Critical (S2)
- **Priority:** High (P1)
- **Environment:** `BUG_MODE=true` or `BUG_003_EXPIRED_TOKEN_ALLOWED=true`
- **Steps to Reproduce:**
  1. Generate JWT with `exp` in the past.
  2. Call `GET /api/v1/transactions` with the expired token in Authorization header.
- **Expected Result:** HTTP 401 Unauthorized: `"token has expired"`.
- **Actual Result:** HTTP 200 OK returned with sensitive transaction records.
- **Status:** Documented / Reproducible in BUG_MODE.

---

### BUG-004: Negative Amount Transfer Credits Sender's Account
- **ID:** BUG-004
- **Title:** Transfer validation fails to enforce strictly positive amounts, enabling balance inflation.
- **Component:** `TransferService` (`transfer_service.py`)
- **Severity:** Blocker (S1)
- **Priority:** High (P1)
- **Environment:** `BUG_MODE=true` or `BUG_004_NEGATIVE_TRANSFER_ALLOWED=true`
- **Steps to Reproduce:**
  1. Call `POST /api/v1/transfers` with `amount = -100.0`.
- **Expected Result:** HTTP 400/422 Bad Request (`"strictly greater than zero"`).
- **Actual Result:** Request returns HTTP 201. Arithmetic `balance - (-100)` increases sender balance by 100!
- **Evidence:** Verified in `test_bug_004_negative_transfer`.
- **Status:** Documented / Reproducible in BUG_MODE.

---

### BUG-005: Pagination Offset Calculation Produces Duplicate Rows
- **ID:** BUG-005
- **Title:** Off-by-one error in pagination offset causes the last item of page N to appear as first item on page N+1.
- **Component:** `TransactionService` (`transaction_service.py`)
- **Severity:** Medium (S3)
- **Priority:** Medium (P2)
- **Environment:** `BUG_MODE=true` or `BUG_005_PAGINATION_DUPLICATES=true`
- **Steps to Reproduce:**
  1. Query `GET /api/v1/transactions?page=1&page_size=5`.
  2. Query `GET /api/v1/transactions?page=2&page_size=5`.
- **Expected Result:** Distinct, disjoint sets of transaction IDs.
- **Actual Result:** Item at index 5 of page 1 is duplicated as item 1 on page 2.
- **Status:** Documented / Reproducible in BUG_MODE.

---

### BUG-006: Self-Transfer Allowed Bypassing Validation Check
- **ID:** BUG-006
- **Title:** Users can initiate transfers to their own email address, generating spurious audit entries.
- **Component:** `TransferService` (`transfer_service.py`)
- **Severity:** Medium (S3)
- **Priority:** Medium (P3)
- **Environment:** `BUG_MODE=true` or `BUG_006_SELF_TRANSFER_ALLOWED=true`
- **Steps to Reproduce:**
  1. Call `POST /api/v1/transfers` where `receiver_email` matches authenticated user email.
- **Expected Result:** HTTP 400 Bad Request: `"Cannot transfer money to yourself"`.
- **Actual Result:** HTTP 201 Created; funds debited and re-credited to same user.
- **Evidence:** Verified in `test_bug_006_self_transfer`.
- **Status:** Documented / Reproducible in BUG_MODE.

---

### BUG-007: Inverted Exchange Rate in Multi-Currency Conversion
- **ID:** BUG-007
- **Title:** Currency conversion arithmetic applies inverted multiplier, leading to massive financial loss.
- **Component:** `WalletService` (`wallet_service.py`)
- **Severity:** Blocker (S1)
- **Priority:** High (P1)
- **Environment:** `BUG_MODE=true` or `BUG_007_WRONG_CURRENCY_RATE=true`
- **Steps to Reproduce:**
  1. Transfer 100 USD to a EUR wallet (Expected: 92.00 EUR at rate 0.92).
- **Expected Result:** Receiver gets 92.00 EUR.
- **Actual Result:** Inverted rate applied (1 / 0.92 = 1.086), receiver gets 108.60 EUR!
- **Status:** Documented / Reproducible in BUG_MODE.

---

### BUG-008: Transaction Remains Stuck in PENDING After Successful Webhook
- **ID:** BUG-008
- **Title:** Webhook processing succeeds but state transition to `SUCCESS` fails to commit to ledger.
- **Component:** `WebhookService` (`webhook_service.py`)
- **Severity:** Critical (S2)
- **Priority:** High (P1)
- **Environment:** `BUG_MODE=true` or `BUG_008_TRANSACTION_STUCK_PENDING=true`
- **Steps to Reproduce:**
  1. Create a PENDING transaction.
  2. Send successful provider webhook.
- **Expected Result:** Transaction status updates to `SUCCESS`.
- **Actual Result:** Transaction status remains indefinitely `PENDING`.
- **Status:** Documented / Reproducible in BUG_MODE.

---

### BUG-009: Locked Account Allowed to Authenticate
- **ID:** BUG-009
- **Title:** Login service fails to verify user `status == LOCKED`, allowing locked accounts to log in.
- **Component:** `AuthService` (`auth_service.py`)
- **Severity:** Critical (S2)
- **Priority:** High (P1)
- **Environment:** `BUG_MODE=true` or `BUG_009_LOCKED_USER_CAN_LOGIN=true`
- **Steps to Reproduce:**
  1. Call `POST /api/v1/auth/login` with credentials of `locked.user@example.com`.
- **Expected Result:** HTTP 403 Forbidden: `"Account is locked"`.
- **Actual Result:** HTTP 200 OK returned with valid JWT access and refresh tokens.
- **Evidence:** Verified in `test_bug_009_locked_user_login`.
- **Status:** Documented / Reproducible in BUG_MODE.

---

### BUG-010: UI Balance Does Not Refresh Following Transfer
- **ID:** BUG-010
- **Title:** Transfer confirmation dialog fails to invalidate React treasury query, displaying stale balance.
- **Component:** Frontend `TransferModal` / `Wallet` View
- **Severity:** Medium (S3)
- **Priority:** Medium (P2)
- **Environment:** `BUG_MODE=true` or `BUG_010_UI_BALANCE_NOT_REFRESHED=true`
- **Steps to Reproduce:**
  1. Open Transfer modal, send $100.00 USD.
  2. Observe Dashboard wallet balance immediately upon modal close.
- **Expected Result:** USD balance immediately decrements by $100.00.
- **Actual Result:** USD balance remains at initial value until manual page reload.
- **Status:** Documented / Reproducible in BUG_MODE.
