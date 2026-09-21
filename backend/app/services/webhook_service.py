import hashlib
import hmac
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import settings
from backend.app.models import ProcessedWebhook, Transaction, Wallet
from backend.app.schemas import PaymentWebhookPayload


class WebhookService:
    @staticmethod
    def generate_signature(event_id: str, transaction_id: str, status_val: str, timestamp: str) -> str:
        msg = f"{event_id}:{transaction_id}:{status_val}:{timestamp}"
        return hmac.new(
            settings.WEBHOOK_SECRET.encode("utf-8"),
            msg.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

    @staticmethod
    def verify_signature(payload: PaymentWebhookPayload) -> bool:
        expected = WebhookService.generate_signature(
            payload.event_id,
            payload.transaction_id,
            payload.status,
            payload.timestamp
        )
        return hmac.compare_digest(expected, payload.signature)

    @staticmethod
    async def process_payment_webhook(db: AsyncSession, payload: PaymentWebhookPayload) -> dict:
        # 1. Verify signature
        if not WebhookService.verify_signature(payload):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature"
            )

        # 2. Check duplicate webhook (BUG-002)
        is_bug_002 = settings.is_bug_active("002_DUPLICATE_WEBHOOK")
        if not is_bug_002:
            res_wh = await db.execute(
                select(ProcessedWebhook).where(ProcessedWebhook.event_id == payload.event_id)
            )
            existing = res_wh.scalar_one_or_none()
            if existing:
                return {
                    "status": "ALREADY_PROCESSED",
                    "message": "Duplicate webhook event ignored",
                    "event_id": payload.event_id,
                    "transaction_id": payload.transaction_id
                }

        # 3. Check transaction exists
        res_txn = await db.execute(
            select(Transaction).where(Transaction.id == payload.transaction_id)
        )
        txn = res_txn.scalar_one_or_none()
        if not txn:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Webhook target transaction {payload.transaction_id} not found"
            )

        # 4. Process status transition (BUG-008)
        is_bug_008 = settings.is_bug_active("008_TRANSACTION_STUCK_PENDING")

        now = datetime.now(timezone.utc)
        if payload.status == "SUCCESS":
            if not is_bug_008:
                txn.status = "SUCCESS"
                txn.completed_at = now
            # If bug 008 is active, status remains PENDING
        elif payload.status == "FAILED":
            txn.status = "FAILED"
            txn.completed_at = now

        # If BUG-002 is active, duplicate processing could also duplicate credit to receiver
        if is_bug_002 and txn.receiver_wallet_id and payload.status == "SUCCESS":
            w_res = await db.execute(select(Wallet).where(Wallet.id == txn.receiver_wallet_id))
            wallet = w_res.scalar_one_or_none()
            if wallet:
                wallet.balance = round(wallet.balance + txn.converted_amount, 2)
                wallet.available_balance = round(wallet.available_balance + txn.converted_amount, 2)

        # Record processed webhook
        import uuid
        proc = ProcessedWebhook(
            id=str(uuid.uuid4()) if is_bug_002 else None,
            event_id=f"{payload.event_id}_{uuid.uuid4().hex[:6]}" if is_bug_002 else payload.event_id,
            transaction_id=payload.transaction_id,
            status=payload.status,
            payload_hash=hashlib.sha256(str(payload.model_dump()).encode("utf-8")).hexdigest()
        )
        db.add(proc)
        await db.commit()

        return {
            "status": "PROCESSED",
            "event_id": payload.event_id,
            "transaction_id": txn.id,
            "transaction_status": txn.status,
            "message": "Webhook processed successfully"
        }
