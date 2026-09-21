# Test Cases Specification: FinPay QA Lab

This document defines formal test cases demonstrating black-box and grey-box test design techniques across all FinPay subsystem boundaries.

---

## 1. Authentication & Session Security

### TC-AUTH-001: Valid User Registration
- **Technique:** Equivalence Partitioning (Valid Inputs)
- **Preconditions:** Database accessible.
- **Steps:**
  1. Send `POST /api/v1/auth/register` with unique email, strong password (>=6 chars), full name.
- **Expected Result:** HTTP 201 Created. User record persisted, 3 multi-currency wallets (USD, EUR, UAH) auto-created, welcome notification issued.

### TC-AUTH-002: Registration with Duplicate Email
- **Technique:** Equivalence Partitioning (Unique Constraint)
- **Steps:**
  1. Submit registration with an email already registered in system.
- **Expected Result:** HTTP 400 Bad Request: `"User with this email already exists"`.

### TC-AUTH-003: Registration Password Boundary Value Analysis
- **Technique:** Boundary Value Analysis (Min Password Length = 6)
- **Test Matrix:**
  - Length 5 (`"12345"`): HTTP 422 Validation Error.
  - Length 6 (`"123456"`): HTTP 201 Created.
  - Length 7 (`"1234567"`): HTTP 201 Created.

### TC-AUTH-004: Account Lockout on 5 Consecutive Failed Logins
- **Technique:** State Transition Testing
- **Steps:**
  1. Submit 4 incorrect passwords for target user -> Expect HTTP 401 Unauthorized (`failed_login_attempts` increments).
  2. Submit 5th incorrect password -> Expect HTTP 403 Forbidden (`status` transitions from `ACTIVE` to `LOCKED`).
  3. Submit 6th attempt with CORRECT password -> Expect HTTP 403 Forbidden (`"Account is locked"`).

### TC-AUTH-005: Refresh Token Rotation & Invalidation
- **Technique:** Security State Invalidation
- **Steps:**
  1. Call `POST /api/v1/auth/refresh` with active refresh token.
  2. Verify HTTP 200 returned with a new access token and rotated refresh token.
  3. Replay old refresh token -> Expect HTTP 401 Unauthorized (`"Invalid or revoked refresh token"`).

---

## 2. Wallet & Treasury Balances

### TC-WAL-001: Multi-Currency Balance Ledger Retrieval
- **Technique:** Schema Validation & Calculation
- **Steps:**
  1. Send `GET /api/v1/wallet` with valid Bearer token.
- **Expected Result:** HTTP 200 OK. Contains wallets array for USD, EUR, and UAH. `total_balance_usd` accurately computed using system conversion rates.

### TC-WAL-002: Unauthorized Wallet Access
- **Technique:** Negative Authorization
- **Steps:**
  1. Send `GET /api/v1/wallet` without `Authorization` header.
- **Expected Result:** HTTP 401 Unauthorized.

---

## 3. Money Transfer Engine

### TC-TRF-001: Standard Valid Transfer (USD to USD)
- **Technique:** Decision Table (DT-1: All Valid)
- **Steps:**
  1. Authenticated user calls `POST /api/v1/transfers` with valid receiver, currency `USD`, amount within available balance.
- **Expected Result:** HTTP 201 Created. Sender balance debited by amount, receiver balance credited by amount, `TRANSFER_SUCCESS` and `TRANSFER_INCOMING` notifications dispatched.

### TC-TRF-002: Transfer Boundary Value Analysis (Available Balance)
- **Technique:** Boundary Value Analysis
- **Sender Balance:** $1000.00
- **Test Scenarios:**
  - Amount = $0.00 -> HTTP 400 Bad Request (`"strictly greater than zero"`).
  - Amount = $0.01 -> HTTP 201 Created ($999.99 remaining).
  - Amount = $999.99 -> HTTP 201 Created ($0.01 remaining).
  - Amount = $1000.00 (Exact Balance) -> HTTP 201 Created ($0.00 remaining).
  - Amount = $1000.01 (1 Cent Overdraft) -> HTTP 400 Bad Request (`"Insufficient available balance"`).

### TC-TRF-003: Idempotency Key Replay Protection
- **Technique:** Idempotent Concurrency Validation
- **Steps:**
  1. Send transfer request with `idempotency_key = "idem_unique_test_01"`.
  2. Record transaction ID and sender balance.
  3. Replay exact same request with identical idempotency key.
- **Expected Result:** HTTP 200/201 returning cached transaction response. Sender is NOT debited a second time.

### TC-TRF-004: Self-Transfer Prevention
- **Technique:** Business Invariant Rule
- **Steps:**
  1. Authenticated user attempts transfer where `receiver_email` equals their own login email.
- **Expected Result:** HTTP 400 Bad Request: `"Cannot transfer money to yourself"`.

---

## 4. Virtual Cards

### TC-CRD-001: Virtual Card Issuance & Masking
- **Technique:** Security Verification
- **Steps:**
  1. Call `POST /api/v1/cards` with cardholder name and spending limit.
- **Expected Result:** HTTP 201 Created. Card number returned in masked format (`**** **** **** 1234`). Plain PAN is never returned or stored unmasked.

### TC-CRD-002: Card Freeze and Unfreeze State Machine
- **Technique:** State Transition Testing
- **Steps:**
  1. Active Card -> `PATCH /api/v1/cards/{id}/freeze` -> HTTP 200 (Status: `FROZEN`).
  2. Frozen Card -> `PATCH /api/v1/cards/{id}/freeze` -> HTTP 400 (`"Card is already frozen"`).
  3. Frozen Card -> `PATCH /api/v1/cards/{id}/unfreeze` -> HTTP 200 (Status: `ACTIVE`).
  4. Active Card -> `DELETE /api/v1/cards/{id}` -> HTTP 204 (Status: `DELETED`).
  5. Deleted Card -> `PATCH /api/v1/cards/{id}/freeze` -> HTTP 404 (`"Card not found"`).

---

## 5. Webhooks & External Payment Provider Mock

### TC-WHK-001: Payment Webhook Signature Verification
- **Technique:** Cryptographic Authentication
- **Steps:**
  1. Calculate valid HMAC SHA-256 signature using shared secret.
  2. Dispatch `POST /api/v1/webhooks/payment`.
- **Expected Result:** HTTP 200 OK (`status = "PROCESSED"`).

### TC-WHK-002: Duplicate Webhook Delivery Protection
- **Technique:** Idempotency & De-duplication
- **Steps:**
  1. Dispatch payment webhook with `event_id = "evt_dedup_01"`.
  2. Dispatch duplicate payment webhook with identical `event_id`.
- **Expected Result:** Second request returns HTTP 200 with `status = "ALREADY_PROCESSED"`. Ledger balance is NOT credited twice.
