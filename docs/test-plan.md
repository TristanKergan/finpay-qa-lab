# Master Test Plan: FinPay QA Lab

## 1. Introduction & Objectives
The goal of the **FinPay QA Lab** test engineering effort is to ensure the absolute correctness, financial integrity, security, and performance of the FinPay fintech platform. Because this is a financial system handling multi-currency balances, peer-to-peer transfers, virtual card lifecycles, and external webhook integrations, the cost of defects (e.g. double spending, race conditions, negative balances, authentication bypasses) is critical.

### Quality Objectives
- **Zero Double-Debiting:** Guarantee strict idempotency across transfer requests and external webhook deliveries under both sequential and simultaneous concurrent requests.
- **ACID Balance Conservation:** Total funds debited from sender must equal funds credited to receiver (accounting for configured conversion rates) without drift, guarded by database constraints and row locking.
- **Access Control & Privacy:** Complete isolation of sensitive customer data and virtual cards (zero IDOR vulnerabilities across transactions, cards, and wallets).
- **Sub-Second Performance:** P95 response times under 300ms for treasury balance queries and transfers under normal load.

---

## 2. Scope of Testing

### In Scope
- **API Functional & Negative Testing:** 31 REST endpoint tests across Auth, Wallet, Transfers, Transactions, Cards, Notifications, and Webhooks.
- **UI End-to-End Automation:** 12 Playwright test methods (15 assertions) across critical user workflows (registration, login/logout, card creation/freeze, notifications, transaction pagination, transfer execution, insufficient funds) in headless mode.
- **Database & Data Consistency:** 4 direct SQL tests verifying balance conservation, atomic rollbacks, user currency unique constraints, and idempotency key uniqueness.
- **Concurrent Transfers & Race Conditions:** Multi-threaded simultaneous execution testing idempotency collisions and balance overdraft race conditions.
- **Security Baseline:** 9 security tests covering IDOR protection on cards/transactions, JWT tampering, stored XSS escaping, and SQL injection resistance across multiple payloads.
- **Defect Injection (`BUG_MODE`):** 10 automated integration tests covering the complete defect matrix (`BUG-001` through `BUG-010`) in both normal and bug mode.
- **Performance:** k6 smoke, load, and stress scenarios benchmarking latency and throughput.

### Out of Scope
- Real fiat banking networks or ACH/SEPA clearance (all transactions execute on simulated sandbox ledger).
- Real payment card physical networks (Visa/Mastercard production networks).
- External live market exchange rate streaming (static configured rates are used).

---

## 3. Test Levels & Environment

| Level | Framework | Test Count | Target |
|---|---|---|---|
| **API Integration** | pytest, httpx, Allure | 31 tests | Status codes, error responses, headers, validation |
| **Database ACID** | pytest, SQLAlchemy 2.0 | 4 tests | Direct DB assertions, balance conservation, constraints |
| **Integration & Defect Matrix** | pytest, threading | 13 tests | Concurrent transfers, E2E lifecycles, BUG-001..BUG-010 |
| **Security & Access Control** | pytest, requests | 9 tests | IDOR, JWT tampering, SQLi payloads, XSS escaping |
| **UI End-to-End** | Playwright (Python POM) | 12 tests | Cross-browser headless flows, failure screenshots & traces |
| **Total Automated Suite** | **pytest orchestrator** | **69 tests** | **100% automated regression pass rate** |
| **Performance** | Grafana k6 | 3 scenarios | Throughput, latency thresholds (p95 < 300ms) |

### Test Environments
- **Local Dev:** SQLite (`sqlite+aiosqlite:///finpay.db`) for instant zero-dependency test execution.
- **Docker Compose / CI:** PostgreSQL 16 Alpine, multi-stage backend and frontend containers.

---

## 4. Entry and Exit Criteria

### Entry Criteria
- Backend compiles and passes schema linting (`ruff check .`).
- Database migrations execute without errors (`alembic upgrade head`).
- Seed data initialized with 5 deterministic test personas.

### Exit Criteria
- 100% passing API automated test suite.
- 100% passing Playwright UI tests with zero flakiness.
- All 10 defects in `docs/bug-reports.md` documented and verified reproducible when `BUG_MODE=true`.
- Allure test report generated with zero failures.
