from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.deps import get_current_user
from backend.app.core.database import get_db
from backend.app.models import User
from backend.app.schemas import TransferCreateRequest, TransferResponse
from backend.app.services.transaction_service import TransactionService
from backend.app.services.transfer_service import TransferService

router = APIRouter(prefix="/transfers", tags=["Transfers"])


@router.post("", response_model=TransferResponse, status_code=status.HTTP_201_CREATED)
async def create_transfer(
    req: TransferCreateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await TransferService.create_transfer(db, user, req)


@router.get("/{id}", response_model=TransferResponse)
async def get_transfer_by_id(
    id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    txn = await TransactionService.get_transaction_by_id(db, user, id)
    return TransferResponse(
        transaction_id=txn.id,
        status=txn.status,
        sender_email=txn.sender_email or "unknown",
        receiver_email=txn.receiver_email or "unknown",
        amount=txn.amount,
        currency=txn.currency,
        converted_amount=txn.converted_amount,
        target_currency=txn.target_currency,
        exchange_rate=txn.exchange_rate,
        idempotency_key=txn.idempotency_key,
        created_at=txn.created_at,
        message=f"Transfer status: {txn.status}"
    )
