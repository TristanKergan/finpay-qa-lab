import asyncio
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from backend.app.core.database import AsyncSessionLocal, init_db
from backend.app.core.security import get_password_hash
from backend.app.models import Card, Notification, Transaction, User, Wallet


async def seed():
    print("🌱 Seeding FinPay QA Lab database...")
    await init_db()

    async with AsyncSessionLocal() as session:
        # Check if already seeded
        res = await session.execute(select(User).where(User.email == "john.doe@example.com"))
        if res.scalar_one_or_none():
            print("Database already contains seed data. Skipping.")
            return

        now = datetime.now(timezone.utc)
        pwd_hash = get_password_hash("Password123!")

        # 1. Create 5 Users
        users_data = [
            {"email": "john.doe@example.com", "full_name": "John Doe", "phone": "+1-555-0101", "status": "ACTIVE"},
            {"email": "jane.smith@example.com", "full_name": "Jane Smith", "phone": "+1-555-0102", "status": "ACTIVE"},
            {"email": "alex.wilson@example.com", "full_name": "Alex Wilson", "phone": "+1-555-0103", "status": "ACTIVE"},
            {"email": "locked.user@example.com", "full_name": "Locked Account", "phone": "+1-555-0104", "status": "LOCKED", "failed_attempts": 5},
            {"email": "qa.tester@example.com", "full_name": "QA Automation Tester", "phone": "+1-555-0105", "status": "ACTIVE"},
        ]

        users = {}
        for u in users_data:
            user = User(
                email=u["email"],
                hashed_password=pwd_hash,
                full_name=u["full_name"],
                phone=u.get("phone"),
                status=u["status"],
                failed_login_attempts=u.get("failed_attempts", 0),
                created_at=now - timedelta(days=30),
            )
            session.add(user)
            await session.flush()
            users[u["email"]] = user

        # 2. Create Wallets across USD, EUR, UAH
        balances = {
            "john.doe@example.com": {"USD": 5000.0, "EUR": 2500.0, "UAH": 50000.0},
            "jane.smith@example.com": {"USD": 3200.0, "EUR": 1800.0, "UAH": 20000.0},
            "alex.wilson@example.com": {"USD": 1500.0, "EUR": 900.0, "UAH": 10000.0},
            "locked.user@example.com": {"USD": 500.0, "EUR": 300.0, "UAH": 5000.0},
            "qa.tester@example.com": {"USD": 10000.0, "EUR": 8000.0, "UAH": 150000.0},
        }

        user_wallets = {}
        for email, curr_balances in balances.items():
            user = users[email]
            user_wallets[email] = {}
            for curr, bal in curr_balances.items():
                w = Wallet(
                    user_id=user.id,
                    currency=curr,
                    balance=bal,
                    available_balance=bal,
                    created_at=now - timedelta(days=30),
                )
                session.add(w)
                await session.flush()
                user_wallets[email][curr] = w

        # 3. Create Virtual Cards
        cards = [
            Card(
                user_id=users["john.doe@example.com"].id,
                card_number_masked="**** **** **** 4242",
                cardholder_name="JOHN DOE",
                expiry_date="12/28",
                card_type="DEBIT",
                status="ACTIVE",
                spending_limit=2500.0,
                created_at=now - timedelta(days=20),
            ),
            Card(
                user_id=users["john.doe@example.com"].id,
                card_number_masked="**** **** **** 5555",
                cardholder_name="JOHN DOE",
                expiry_date="08/27",
                card_type="VIRTUAL",
                status="FROZEN",
                spending_limit=500.0,
                created_at=now - timedelta(days=15),
            ),
            Card(
                user_id=users["qa.tester@example.com"].id,
                card_number_masked="**** **** **** 8888",
                cardholder_name="QA TESTER",
                expiry_date="11/29",
                card_type="CREDIT",
                status="ACTIVE",
                spending_limit=5000.0,
                created_at=now - timedelta(days=10),
            ),
        ]
        session.add_all(cards)

        # 4. Create Diverse Transactions (Different currencies & statuses)
        txns = [
            # Successful transfer USD
            Transaction(
                sender_id=users["john.doe@example.com"].id,
                receiver_id=users["jane.smith@example.com"].id,
                sender_wallet_id=user_wallets["john.doe@example.com"]["USD"].id,
                receiver_wallet_id=user_wallets["jane.smith@example.com"]["USD"].id,
                amount=250.0,
                currency="USD",
                converted_amount=250.0,
                target_currency="USD",
                exchange_rate=1.0,
                status="SUCCESS",
                idempotency_key="seed-txn-001-usd-success",
                description="Dinner & groceries split",
                created_at=now - timedelta(days=5),
                completed_at=now - timedelta(days=5),
            ),
            # Successful transfer EUR
            Transaction(
                sender_id=users["jane.smith@example.com"].id,
                receiver_id=users["alex.wilson@example.com"].id,
                sender_wallet_id=user_wallets["jane.smith@example.com"]["EUR"].id,
                receiver_wallet_id=user_wallets["alex.wilson@example.com"]["EUR"].id,
                amount=120.0,
                currency="EUR",
                converted_amount=120.0,
                target_currency="EUR",
                exchange_rate=1.0,
                status="SUCCESS",
                idempotency_key="seed-txn-002-eur-success",
                description="Consulting invoice settlement",
                created_at=now - timedelta(days=3),
                completed_at=now - timedelta(days=3),
            ),
            # Pending transfer
            Transaction(
                sender_id=users["alex.wilson@example.com"].id,
                receiver_id=users["john.doe@example.com"].id,
                sender_wallet_id=user_wallets["alex.wilson@example.com"]["USD"].id,
                receiver_wallet_id=user_wallets["john.doe@example.com"]["USD"].id,
                amount=75.0,
                currency="USD",
                converted_amount=75.0,
                target_currency="USD",
                exchange_rate=1.0,
                status="PENDING",
                idempotency_key="seed-txn-003-usd-pending",
                description="Pending wire reimbursement",
                created_at=now - timedelta(hours=4),
                completed_at=None,
            ),
            # Failed transfer
            Transaction(
                sender_id=users["john.doe@example.com"].id,
                receiver_id=users["locked.user@example.com"].id,
                sender_wallet_id=user_wallets["john.doe@example.com"]["UAH"].id,
                receiver_wallet_id=user_wallets["locked.user@example.com"]["UAH"].id,
                amount=1500.0,
                currency="UAH",
                converted_amount=1500.0,
                target_currency="UAH",
                exchange_rate=1.0,
                status="FAILED",
                idempotency_key="seed-txn-004-uah-failed",
                description="Transfer to locked receiver (simulated rejection)",
                created_at=now - timedelta(days=2),
                completed_at=now - timedelta(days=2),
            ),
            # Cancelled transfer
            Transaction(
                sender_id=users["qa.tester@example.com"].id,
                receiver_id=users["jane.smith@example.com"].id,
                sender_wallet_id=user_wallets["qa.tester@example.com"]["USD"].id,
                receiver_wallet_id=user_wallets["jane.smith@example.com"]["USD"].id,
                amount=50.0,
                currency="USD",
                converted_amount=50.0,
                target_currency="USD",
                exchange_rate=1.0,
                status="CANCELLED",
                idempotency_key="seed-txn-005-usd-cancelled",
                description="Cancelled test order",
                created_at=now - timedelta(days=1),
                completed_at=now - timedelta(days=1),
            ),
        ]
        session.add_all(txns)

        # 5. Create Notifications
        notes = [
            Notification(
                user_id=users["john.doe@example.com"].id,
                type="TRANSFER_SUCCESS",
                title="Transfer Successful",
                message="Successfully transferred 250.00 USD to Jane Smith.",
                is_read=True,
                created_at=now - timedelta(days=5),
            ),
            Notification(
                user_id=users["jane.smith@example.com"].id,
                type="TRANSFER_INCOMING",
                title="Payment Received",
                message="Received 250.00 USD from John Doe.",
                is_read=False,
                created_at=now - timedelta(days=5),
            ),
            Notification(
                user_id=users["john.doe@example.com"].id,
                type="CARD_FROZEN",
                title="Card Frozen",
                message="Virtual card ending in 5555 has been frozen.",
                is_read=False,
                created_at=now - timedelta(days=15),
            ),
            Notification(
                user_id=users["locked.user@example.com"].id,
                type="ACCOUNT_LOCKED",
                title="Security Alert",
                message="Account locked after 5 consecutive failed login attempts.",
                is_read=False,
                created_at=now - timedelta(days=28),
            ),
        ]
        session.add_all(notes)

        await session.commit()
        print("✅ Database successfully seeded with 5 users, multi-currency wallets, cards, transactions, and notifications!")


if __name__ == "__main__":
    asyncio.run(seed())
