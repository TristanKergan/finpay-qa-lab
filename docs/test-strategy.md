# Test Strategy: FinPay QA Lab

## 1. Quality Philosophy: The Test Pyramid
FinPay QA Lab follows a structured test pyramid designed for high confidence, fast feedback, and minimal maintenance cost:

```
          / \
         / UI \          ~15% (11 Critical Playwright E2E User Flows)
        /------\
       / Integr \        ~25% (Multi-step Lifecycles, Webhook Replays, BUG_MODE)
      /----------\
     /    API     \      ~45% (HTTP Status Codes, Schemas, Auth, Boundary Values)
    /--------------\
   / Database / Unit\    ~15% (Direct SQL Assertions, ACID Balances, Constraints)
  --------------------
```

---

## 2. Test Design Techniques Applied

### A. Equivalence Partitioning (EP)
- **Transfer Amounts:**
  - Class A (Valid): Strictly positive amounts within available balance `(0 < amount <= available_balance)`.
  - Class B (Overdraft): Amounts exceeding available balance `(amount > available_balance)` -> 400 Bad Request.
  - Class C (Non-positive): Amounts `<= 0` -> 400 / 422 Validation Error.
- **Supported Currencies:**
  - Valid: `USD`, `EUR`, `UAH`.
  - Invalid: `GBP`, `BTC`, `XYZ` -> 422 Unprocessable Entity.

### B. Boundary Value Analysis (BVA)
- **Transfer Amount Boundaries:**
  - `0.00` (Boundary - Invalid) -> Rejected.
  - `0.01` (Minimum valid unit) -> Accepted.
  - `available_balance - 0.01` (Near max) -> Accepted.
  - `available_balance` (Exact max) -> Accepted.
  - `available_balance + 0.01` (Overdraft by 1 cent) -> Rejected.

### C. Decision Table Testing (Transfers Engine)

| Rule # | Auth Valid | Sender Active | Receiver Exists | Balance Sufficient | Sender != Receiver | Expected HTTP | Outcome |
|---|---|---|---|---|---|---|---|
| **DT-1** | Yes | Yes | Yes | Yes | Yes | 201 Created | Success & debited |
| **DT-2** | No | — | — | — | — | 401 Unauthorized | Blocked |
| **DT-3** | Yes | Locked | — | — | — | 403 Forbidden | Blocked |
| **DT-4** | Yes | Yes | No | — | — | 404 Not Found | Blocked |
| **DT-5** | Yes | Yes | Yes | No | Yes | 400 Bad Request | Insufficient balance |
| **DT-6** | Yes | Yes | Yes | Yes | No (Self) | 400 Bad Request | Self-transfer disallowed |

### D. State Transition Testing
- **Transaction Lifecycle:**
  `[INITIATED]` -> `[PROCESSING]` -> `[SUCCESS]` (Terminal, Immutable)
                                 -> `[FAILED]` (Terminal)
                                 -> `[CANCELLED]` (Terminal)
- **Card Lifecycle:**
  `[CREATED / ACTIVE]` <-> `[FROZEN]` -> `[DELETED]` (Terminal)

---

## 3. Automation Framework Architecture

- **Page Object Model (POM):** Decouples UI locator selectors from test assertions. All page actions encapsulated in `tests/pages/`.
- **API Facade (`FinPayApiClient`):** Fluent, reusable HTTP client attaching all request/response bodies and status codes to Allure.
- **Flakiness Safeguards:**
  - Avoid hard sleeps; use Playwright explicit event listeners (`wait_for_selector(..., state="visible")`).
  - Isolated test data generation via `UserFactory` using Faker.
  - Database rollback checkpoints.
