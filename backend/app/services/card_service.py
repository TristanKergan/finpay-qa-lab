import random
from datetime import datetime, timezone
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from backend.app.models import Card, Notification, User
from backend.app.schemas import CardCreateRequest, CardResponse


class CardService:
    @staticmethod
    def _generate_masked_card_number() -> str:
        last4 = random.randint(1000, 9999)
        return f"**** **** **** {last4}"

    @staticmethod
    def _generate_expiry_date() -> str:
        now = datetime.now()
        year = (now.year + 3) % 100
        month = random.randint(1, 12)
        return f"{month:02d}/{year:02d}"

    @staticmethod
    async def create_card(db: AsyncSession, user: User, req: CardCreateRequest) -> CardResponse:
        card = Card(
            user_id=user.id,
            card_number_masked=CardService._generate_masked_card_number(),
            cardholder_name=req.cardholder_name.upper(),
            expiry_date=CardService._generate_expiry_date(),
            card_type=req.card_type,
            status="ACTIVE",
            spending_limit=req.spending_limit,
        )
        db.add(card)

        note = Notification(
            user_id=user.id,
            type="CARD_CREATED",
            title="Virtual Card Created",
            message=f"Your new virtual card ending in {card.card_number_masked[-4:]} is active.",
        )
        db.add(note)

        await db.commit()
        await db.refresh(card)
        return CardResponse.model_validate(card)

    @staticmethod
    async def get_user_cards(db: AsyncSession, user: User) -> List[CardResponse]:
        res = await db.execute(
            select(Card).where(Card.user_id == user.id, Card.status != "DELETED").order_by(Card.created_at.desc())
        )
        cards = res.scalars().all()
        return [CardResponse.model_validate(c) for c in cards]

    @staticmethod
    async def freeze_card(db: AsyncSession, user: User, card_id: str) -> CardResponse:
        res = await db.execute(select(Card).where(Card.id == card_id))
        card = res.scalar_one_or_none()
        if not card or card.status == "DELETED":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
        if card.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to modify this card")
        if card.status == "FROZEN":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Card is already frozen")

        card.status = "FROZEN"
        note = Notification(
            user_id=user.id,
            type="CARD_FROZEN",
            title="Card Frozen",
            message=f"Virtual card ending in {card.card_number_masked[-4:]} was frozen.",
        )
        db.add(note)
        await db.commit()
        await db.refresh(card)
        return CardResponse.model_validate(card)

    @staticmethod
    async def unfreeze_card(db: AsyncSession, user: User, card_id: str) -> CardResponse:
        res = await db.execute(select(Card).where(Card.id == card_id))
        card = res.scalar_one_or_none()
        if not card or card.status == "DELETED":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
        if card.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to modify this card")
        if card.status == "ACTIVE":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Card is already active")

        card.status = "ACTIVE"
        await db.commit()
        await db.refresh(card)
        return CardResponse.model_validate(card)

    @staticmethod
    async def delete_card(db: AsyncSession, user: User, card_id: str):
        res = await db.execute(select(Card).where(Card.id == card_id))
        card = res.scalar_one_or_none()
        if not card or card.status == "DELETED":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
        if card.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this card")

        card.status = "DELETED"
        await db.commit()
