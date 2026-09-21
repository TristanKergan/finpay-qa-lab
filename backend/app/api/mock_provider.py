from fastapi import APIRouter

from backend.app.schemas import MockPaymentProcessRequest
from backend.app.services.mock_payment_service import MockPaymentService

router = APIRouter(prefix="/mock/payment", tags=["Simulated Payment Provider"])


@router.post("/process")
async def process_simulated_payment(req: MockPaymentProcessRequest):
    return await MockPaymentService.process_mock_payment(req)
