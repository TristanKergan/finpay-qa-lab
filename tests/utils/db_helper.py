from typing import Optional
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import AsyncSessionLocal
from backend.app.models import Transaction, User, Wallet


class DbHelper:
    @staticmethod
    async def get_user_by_email(email: str) -> Optional[User]:
        async with AsyncSessionLocal() as session:
            res = await session.execute(select(User).where(User.email == email.lower()))
            return res.scalar_one_or_none()

    @staticmethod
    async def get_wallet_balance(user_id: str, currency: str) -> Optional[tuple[float, float]]:
        """Returns (balance, available_balance)"""
        async with AsyncSessionLocal() as session:
            res = await session.execute(
                select(Wallet.balance, Wallet.available_balance).where(
                    Wallet.user_id == user_id,
                    Wallet.currency == currency
                )
            )
            return res.first()

    @staticmethod
    async def count_transactions_by_idempotency_key(idempotency_key: str) -> int:
        async with AsyncSessionLocal() as session:
            res = await session.execute(
                select(Transaction).where(Transaction.idempotency_key == idempotency_key)
            )
            return len(res.scalars().all())

    @staticmethod
    async def execute_raw_sql(sql: str, params: dict = None):
        async with AsyncSessionLocal() as session:
            res = await session.execute(text(sql), params or {})
            await session.commit()
            return res
