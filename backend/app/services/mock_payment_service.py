import uuid
from datetime import datetime, timezone
from fastapi import HTTPException, status
from backend.app.schemas import MockPaymentProcessRequest, MockPaymentProcessResponse
from backend.app.services.webhook_service import WebhookService


class MockPaymentService:
    @staticmethod
    async def process_mock_payment(req: MockPaymentProcessRequest) -> dict:
        if req.scenario == "TIMEOUT":
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Payment provider gateway timeout during processing"
            )

        if req.scenario == "DUPLICATE":
            event_id = f"evt_fixed_duplicate_for_{req.transaction_id}"
        else:
            event_id = f"evt_{uuid.uuid4().hex[:12]}"

        timestamp = datetime.now(timezone.utc).isoformat()
        webhook_status = "SUCCESS" if req.scenario in ["SUCCESS", "DUPLICATE"] else "FAILED"

        signature = WebhookService.generate_signature(
            event_id=event_id,
            transaction_id=req.transaction_id,
            status_val=webhook_status,
            timestamp=timestamp
        )

        return {
            "status": webhook_status,
            "event_id": event_id,
            "transaction_id": req.transaction_id,
            "timestamp": timestamp,
            "signature": signature,
            "message": f"Simulated provider result: {webhook_status}"
        }
