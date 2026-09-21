from typing import List, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.config import settings
from backend.app.models import Wallet
from backend.app.schemas import WalletResponse, WalletSummaryResponse


class WalletService:
    @staticmethod
    def convert_currency(amount: float, from_curr: str, to_curr: str) -> Tuple[float, float]:
        """
        Converts amount from from_curr to to_curr.
        Returns (converted_amount, exchange_rate).
        Handles BUG-007 (inverted exchange rate) when active.
        """
        if from_curr == to_curr:
            return round(amount, 2), 1.0

        rates = settings.EXCHANGE_RATES
        from_rate = rates.get(from_curr, 1.0)
        to_rate = rates.get(to_curr, 1.0)

        # Standard conversion: base is USD
        # USD -> EUR (1 USD * 0.92 = 0.92 EUR)
        # EUR -> USD (1 EUR / 0.92 = 1.086 USD)
        standard_rate = to_rate / from_rate

        # Check BUG-007
        if settings.is_bug_active("007_WRONG_CURRENCY_RATE"):
            # Inverted exchange rate bug
            buggy_rate = from_rate / to_rate
            return round(amount * buggy_rate, 2), round(buggy_rate, 4)

        converted_amount = round(amount * standard_rate, 2)
        return converted_amount, round(standard_rate, 4)

    @staticmethod
    async def get_user_wallets(db: AsyncSession, user_id: str) -> WalletSummaryResponse:
        result = await db.execute(
            select(Wallet).where(Wallet.user_id == user_id).order_by(Wallet.currency)
        )
        wallets = result.scalars().all()
        
        # Calculate total in USD
        total_usd = 0.0
        for w in wallets:
            amt_usd, _ = WalletService.convert_currency(w.balance, w.currency, "USD")
            total_usd += amt_usd

        return WalletSummaryResponse(
            wallets=[WalletResponse.model_validate(w) for w in wallets],
            total_balance_usd=round(total_usd, 2)
        )

    @staticmethod
    async def get_or_create_wallet(db: AsyncSession, user_id: str, currency: str) -> Wallet:
        result = await db.execute(
            select(Wallet).where(Wallet.user_id == user_id, Wallet.currency == currency)
        )
        wallet = result.scalar_one_or_none()
        if not wallet:
            wallet = Wallet(user_id=user_id, currency=currency, balance=0.0, available_balance=0.0)
            db.add(wallet)
            await db.flush()
        return wallet
