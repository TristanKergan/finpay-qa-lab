from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.api.deps import get_current_user
from backend.app.core.database import get_db
from backend.app.models import User
from backend.app.schemas import TransactionListResponse, TransactionResponse
from backend.app.services.transaction_service import TransactionService

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("", response_model=TransactionListResponse)
async def list_transactions(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    status: Optional[str] = Query(default=None),
    currency: Optional[str] = Query(default=None),
    sort_by: str = Query(default="created_at"),
    order: str = Query(default="desc", pattern="^(asc|desc)$"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await TransactionService.get_transactions(
        db=db,
        user=user,
        page=page,
        page_size=page_size,
        status_filter=status,
        currency_filter=currency,
        sort_by=sort_by,
        order=order
    )


@router.get("/{id}", response_model=TransactionResponse)
async def get_transaction(
    id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await TransactionService.get_transaction_by_id(db, user, id)
