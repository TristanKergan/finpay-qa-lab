# Master Test Plan: FinPay QA Lab

## 1. Introduction & Objectives
The goal of the **FinPay QA Lab** test engineering effort is to ensure the absolute correctness, financial integrity, security, and performance of the FinPay fintech platform. Because this is a financial system handling multi-currency balances, peer-to-peer transfers, virtual card lifecycles, and external webhook integrations, the cost of defects (e.g. double spending, race conditions, negative balances, authentication bypasses) is critical.

### Quality Objectives
- **Zero Double-Debiting:** Guarantee strict idempotency across transfer requests and external webhook deliveries.
- **ACID Balance Conservation:** Total funds debited from sender must equal funds credited to receiver (accounting for conversion rates) without drift.
- **Access Control & Privacy:** Complete isolation of sensitive customer data and virtual cards (zero IDOR vulnerabilities).
- **Sub-Second Performance:** P95 response times under 300ms for treasury balance queries and transfers under normal load.

---

## 2. Scope of Testing

### In Scope
- **API Functional & Negative Testing:** 100% of all public REST endpoints across Auth, Wallet, Transfers, Transactions, Cards, Notifications, and Webhooks.
- **UI End-to-End Automation:** 11 critical user workflows simulated using Playwright in headless CI mode.
- **Database & Data Consistency:** Direct SQL validation verifying transaction states, table constraints, and ACID rollback behaviors.
- **Security Baseline:** IDOR protection, JWT tampering, stored XSS escaping, SQL injection resistance.
- **Defect Injection (`BUG_MODE`):** Automated verification that 10 realistic defects reproduce and can be flagged by the QA suite.
- **Performance:** k6 smoke, load, and stress scenarios.

### Out of Scope
- Real fiat money processing (all transactions use simulated sandbox ledger).
- Real payment card networks (Visa/Mastercard settlement).

---

## 3. Test Levels & Environment

| Level | Framework | Execution Frequency | Target |
|---|---|---|---|
| **Unit & Schema** | pytest, Pydantic v2 | Every commit | Business logic, validators, schemas |
| **API Integration** | pytest, httpx, Allure | Pull Request / CI | Status codes, error responses, headers |
| **Database ACID** | pytest, SQLAlchemy 2.0 | Pull Request / CI | Direct DB assertions, constraint checks |
| **UI End-to-End** | Playwright (Python POM) | Nightly / Release CI | Cross-browser headless flows |
| **Performance** | Grafana k6 | Pre-release / Nightly | Throughput, latency thresholds (p95 < 500ms) |

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
