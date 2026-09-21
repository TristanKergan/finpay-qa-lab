from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.api.deps import get_current_user
from backend.app.core.database import get_db
from backend.app.models import User
from backend.app.schemas import NotificationListResponse, NotificationResponse
from backend.app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await NotificationService.get_user_notifications(db, user)


@router.patch("/{id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await NotificationService.mark_as_read(db, user, id)


@router.post("/read-all")
async def mark_all_read(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    count = await NotificationService.mark_all_as_read(db, user)
    return {"message": f"Marked {count} notifications as read"}
