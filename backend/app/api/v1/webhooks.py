from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db
from backend.app.schemas import PaymentWebhookPayload
from backend.app.services.webhook_service import WebhookService

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/payment")
async def handle_payment_webhook(
    payload: PaymentWebhookPayload,
    db: AsyncSession = Depends(get_db)
):
    return await WebhookService.process_payment_webhook(db, payload)
