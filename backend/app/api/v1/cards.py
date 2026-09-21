
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.deps import get_current_user
from backend.app.core.database import get_db
from backend.app.models import User
from backend.app.schemas import CardCreateRequest, CardResponse
from backend.app.services.card_service import CardService

router = APIRouter(prefix="/cards", tags=["Virtual Cards"])


@router.post("", response_model=CardResponse, status_code=status.HTTP_201_CREATED)
async def create_card(
    req: CardCreateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await CardService.create_card(db, user, req)


@router.get("", response_model=list[CardResponse])
async def list_cards(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await CardService.get_user_cards(db, user)


@router.patch("/{id}/freeze", response_model=CardResponse)
async def freeze_card(
    id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await CardService.freeze_card(db, user, id)


@router.patch("/{id}/unfreeze", response_model=CardResponse)
async def unfreeze_card(
    id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await CardService.unfreeze_card(db, user, id)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_card(
    id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await CardService.delete_card(db, user, id)
