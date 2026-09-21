# Requirements Traceability Matrix (RTM)

| Req ID | Requirement Description | Business Rule | Automated Test File | Test Case ID | Defect Flag |
|---|---|---|---|---|---|
| **REQ-AUTH-01** | User Registration | Must create unique user and 3 wallets | `tests/api/test_auth_api.py` | `TC-AUTH-001` | — |
| **REQ-AUTH-02** | Account Lockout | Locked after 5 failed password attempts | `tests/api/test_auth_api.py` | `TC-AUTH-004` | `BUG-009` |
| **REQ-AUTH-03** | Token Refresh | Rotates refresh token, invalidates old | `tests/api/test_auth_api.py` | `TC-AUTH-005` | — |
| **REQ-WAL-01** | Multi-Currency Wallets | Support USD, EUR, UAH with live totals | `tests/api/test_wallet_api.py` | `TC-WAL-001` | `BUG-007` |
| **REQ-TRF-01** | Transfer Execution | Atomic balance deduction & credit | `tests/api/test_transfers_api.py` | `TC-TRF-001` | — |
| **REQ-TRF-02** | Transfer Idempotency | No duplicate debit on repeated key | `tests/api/test_transfers_api.py` | `TC-TRF-003` | `BUG-001` |
| **REQ-TRF-03** | Negative Amount Blocked | Amount must be strictly positive | `tests/api/test_transfers_api.py` | `TC-TRF-002` | `BUG-004` |
| **REQ-TRF-04** | Self-Transfer Blocked | Sender cannot transfer to self | `tests/api/test_transfers_api.py` | `TC-TRF-004` | `BUG-006` |
| **REQ-CRD-01** | Virtual Card Masking | Mask all PANs except last 4 digits | `tests/api/test_cards_api.py` | `TC-CRD-001` | — |
| **REQ-CRD-02** | Card Freeze / Unfreeze | State transition ACTIVE <-> FROZEN | `tests/api/test_cards_api.py` | `TC-CRD-002` | — |
| **REQ-WHK-01** | Webhook Deduplication | Duplicate event_id must be ignored | `tests/api/test_webhooks_api.py` | `TC-WHK-002` | `BUG-002` |
| **REQ-DB-01** | Balance Conservation | `Sender_loss == Receiver_gain` | `tests/database/test_db_balance_integrity.py` | `TC-DB-001` | — |
| **REQ-UI-01** | E2E Registration Flow | Register from UI into Dashboard | `tests/ui/test_ui_auth.py` | `TC-UI-001` | — |
| **REQ-UI-02** | E2E Money Transfer | Modal form submit updates UI ledger | `tests/ui/test_ui_wallet_and_transfers.py` | `TC-UI-002` | `BUG-010` |
| **REQ-TRF-05** | Concurrent Transfer Idempotency | Simultaneous workers with same key yield exactly 1 debit | `tests/integration/test_concurrent_transfers.py` | `TC-CONC-001` | `BUG-001` |
| **REQ-TRF-06** | Concurrent Overdraft Protection | Competing transfers exceeding funds block overdraft with 400 | `tests/integration/test_concurrent_transfers.py` | `TC-CONC-002` | — |
| **REQ-CRD-03** | ISO/IEC 7812 Luhn Validation | PAN must satisfy Mod 10 checksum | `backend/app/services/card_service.py` | `TC-CRD-003` | — |

