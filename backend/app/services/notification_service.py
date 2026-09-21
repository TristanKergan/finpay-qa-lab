from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models import Notification, User
from backend.app.schemas import NotificationListResponse, NotificationResponse


class NotificationService:
    @staticmethod
    async def get_user_notifications(db: AsyncSession, user: User) -> NotificationListResponse:
        res = await db.execute(
            select(Notification)
            .where(Notification.user_id == user.id)
            .order_by(Notification.created_at.desc())
        )
        notifications = res.scalars().all()

        unread_res = await db.execute(
            select(func.count())
            .select_from(Notification)
            .where(Notification.user_id == user.id, Notification.is_read == False)
        )
        unread_count = unread_res.scalar() or 0

        return NotificationListResponse(
            items=[NotificationResponse.model_validate(n) for n in notifications],
            unread_count=unread_count
        )

    @staticmethod
    async def mark_as_read(db: AsyncSession, user: User, notification_id: str) -> NotificationResponse:
        res = await db.execute(select(Notification).where(Notification.id == notification_id))
        note = res.scalar_one_or_none()
        if not note:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
        if note.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this notification")

        note.is_read = True
        await db.commit()
        await db.refresh(note)
        return NotificationResponse.model_validate(note)

    @staticmethod
    async def mark_all_as_read(db: AsyncSession, user: User) -> int:
        res = await db.execute(
            select(Notification).where(Notification.user_id == user.id, Notification.is_read == False)
        )
        notes = res.scalars().all()
        for n in notes:
            n.is_read = True
        await db.commit()
        return len(notes)
