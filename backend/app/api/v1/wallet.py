from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.deps import get_current_user
from backend.app.core.database import get_db
from backend.app.models import User
from backend.app.schemas import WalletSummaryResponse
from backend.app.services.wallet_service import WalletService

router = APIRouter(prefix="/wallet", tags=["Wallet"])


@router.get("", response_model=WalletSummaryResponse)
async def get_wallet_summary(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await WalletService.get_user_wallets(db, user.id)
