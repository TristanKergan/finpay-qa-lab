import asyncio
from collections import defaultdict
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import settings
from backend.app.models import Notification, Transaction, User, Wallet
from backend.app.schemas import TransferCreateRequest, TransferResponse
from backend.app.services.wallet_service import WalletService

_user_transfer_locks: dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)


class TransferService:
    @staticmethod
    async def create_transfer(
        db: AsyncSession,
        sender: User,
        req: TransferCreateRequest
    ) -> TransferResponse:
        sender_id = sender.id
        sender_email = sender.email
        sender_name = sender.full_name

        async with _user_transfer_locks[sender_id]:
            # 1. Check sender status
            if sender.status == "LOCKED":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Account is locked. Cannot perform transactions."
                )
            if sender.status != "ACTIVE":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Account is inactive or suspended."
                )

            # 2. Check transfer amount (BUG-004)
            is_bug_004 = settings.is_bug_active("004_NEGATIVE_TRANSFER_ALLOWED")
            if not is_bug_004 and req.amount <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Transfer amount must be strictly greater than zero"
                )

            # 3. Check self-transfer (BUG-006)
            is_bug_006 = settings.is_bug_active("006_SELF_TRANSFER_ALLOWED")
            if not is_bug_006 and sender_email.lower() == req.receiver_email.lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot transfer money to yourself"
                )

            # 4. Check idempotency key (BUG-001)
            is_bug_001 = settings.is_bug_active("001_DUPLICATE_TRANSFER")
            if req.idempotency_key and not is_bug_001:
                existing_txn_res = await db.execute(
                    select(Transaction).where(Transaction.idempotency_key == req.idempotency_key)
                )
                existing_txn = existing_txn_res.scalar_one_or_none()
                if existing_txn:
                    receiver_res = await db.execute(select(User.email).where(User.id == existing_txn.receiver_id))
                    rec_email = receiver_res.scalar_one_or_none() or "unknown"
                    return TransferResponse(
                        transaction_id=existing_txn.id,
                        status=existing_txn.status,
                        sender_email=sender_email,
                        receiver_email=rec_email,
                        amount=existing_txn.amount,
                        currency=existing_txn.currency,
                        converted_amount=existing_txn.converted_amount,
                        target_currency=existing_txn.target_currency,
                        exchange_rate=existing_txn.exchange_rate,
                        idempotency_key=existing_txn.idempotency_key,
                        created_at=existing_txn.created_at,
                        message="Idempotent replay: transaction already processed",
                        suppress_refresh=False,
                    )

            # 5. Check receiver
            receiver_res = await db.execute(select(User).where(User.email == req.receiver_email))
            receiver = receiver_res.scalar_one_or_none()
            if not receiver:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Receiver user not found"
                )
            if receiver.status != "ACTIVE":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Receiver account is not active or is locked"
                )

            # 6. Check sender wallet (with pessimistic row locking on Postgres)
            sender_wallet_query = select(Wallet).where(
                Wallet.user_id == sender_id,
                Wallet.currency == req.currency
            )
            if not settings.DATABASE_URL.startswith("sqlite"):
                sender_wallet_query = sender_wallet_query.with_for_update()
            sender_wallet_res = await db.execute(sender_wallet_query)
            sender_wallet = sender_wallet_res.scalar_one_or_none()
            if not sender_wallet:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Sender does not have a {req.currency} wallet"
                )

            if sender_wallet.available_balance < req.amount:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient available balance. Required: {req.amount} {req.currency}, Available: {sender_wallet.available_balance} {req.currency}"
                )

            # 7. Receiver wallet & Currency conversion
            receiver_wallet = await WalletService.get_or_create_wallet(db, receiver.id, req.currency)
            converted_amount, exchange_rate = WalletService.convert_currency(
                req.amount, req.currency, receiver_wallet.currency
            )

            now = datetime.now(timezone.utc)

            # 8. Perform atomic balance updates
            sender_wallet.balance = round(sender_wallet.balance - req.amount, 2)
            sender_wallet.available_balance = round(sender_wallet.available_balance - req.amount, 2)

            receiver_wallet.balance = round(receiver_wallet.balance + converted_amount, 2)
            receiver_wallet.available_balance = round(receiver_wallet.available_balance + converted_amount, 2)

            # 9. Create Transaction
            txn = Transaction(
                sender_id=sender_id,
                receiver_id=receiver.id,
                sender_wallet_id=sender_wallet.id,
                receiver_wallet_id=receiver_wallet.id,
                amount=req.amount,
                currency=req.currency,
                converted_amount=converted_amount,
                target_currency=receiver_wallet.currency,
                exchange_rate=exchange_rate,
                status="SUCCESS",
                idempotency_key=None if is_bug_001 else req.idempotency_key,
                description=req.description,
                created_at=now,
                completed_at=now,
            )
            # Check BUG-010 (UI balance not refreshed)
            is_bug_010 = settings.is_bug_active("010_UI_BALANCE_NOT_REFRESHED")

            try:
                db.add(txn)
                # 10. Create Notifications
                sender_note = Notification(
                    user_id=sender_id,
                    type="TRANSFER_SUCCESS",
                    title="Money Sent",
                    message=f"Successfully transferred {req.amount} {req.currency} to {receiver.full_name} ({receiver.email}).",
                    created_at=now,
                )
                receiver_note = Notification(
                    user_id=receiver.id,
                    type="TRANSFER_INCOMING",
                    title="Money Received",
                    message=f"Received {converted_amount} {receiver_wallet.currency} from {sender_name} ({sender_email}).",
                    created_at=now,
                )
                db.add_all([sender_note, receiver_note])

                await db.commit()
                await db.refresh(txn)
            except IntegrityError:
                await db.rollback()
                # Race condition caught by DB unique constraint on idempotency_key
                if req.idempotency_key and not is_bug_001:
                    winning_txn = None
                    for _ in range(15):
                        winning_txn_res = await db.execute(
                            select(Transaction).where(Transaction.idempotency_key == req.idempotency_key)
                        )
                        winning_txn = winning_txn_res.scalar_one_or_none()
                        if winning_txn:
                            break
                        await asyncio.sleep(0.05)

                    if winning_txn:
                        receiver_res = await db.execute(select(User.email).where(User.id == winning_txn.receiver_id))
                        rec_email = receiver_res.scalar_one_or_none() or "unknown"
                        return TransferResponse(
                            transaction_id=winning_txn.id,
                            status=winning_txn.status,
                            sender_email=sender_email,
                            receiver_email=rec_email,
                            amount=winning_txn.amount,
                            currency=winning_txn.currency,
                            converted_amount=winning_txn.converted_amount,
                            target_currency=winning_txn.target_currency,
                            exchange_rate=winning_txn.exchange_rate,
                            idempotency_key=winning_txn.idempotency_key,
                            created_at=winning_txn.created_at,
                            message="Idempotent replay: concurrent transaction completed",
                            suppress_refresh=is_bug_010,
                        )
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Transaction conflict: concurrent operation detected",
                )

            return TransferResponse(
                transaction_id=txn.id,
                status=txn.status,
                sender_email=sender_email,
                receiver_email=receiver.email,
                amount=txn.amount,
                currency=txn.currency,
                converted_amount=txn.converted_amount,
                target_currency=txn.target_currency,
                exchange_rate=txn.exchange_rate,
                idempotency_key=txn.idempotency_key,
                created_at=txn.created_at,
                message="Transfer processed successfully",
                suppress_refresh=is_bug_010,
            )
