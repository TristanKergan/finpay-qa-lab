import random
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models import Card, Notification, User
from backend.app.schemas import CardCreateRequest, CardResponse


class CardService:
    @staticmethod
    def generate_luhn_pan(bin_prefix: str = "4532") -> str:
        """Generates a 16-digit Primary Account Number (PAN) conforming to ISO/IEC 7812 Luhn checksum."""
        digits = [int(d) for d in bin_prefix]
        while len(digits) < 15:
            digits.append(random.randint(0, 9))

        # Calculate Luhn check digit
        total = 0
        for idx, digit in enumerate(reversed(digits)):
            if idx % 2 == 0:
                doubled = digit * 2
                total += doubled - 9 if doubled > 9 else doubled
            else:
                total += digit
        check_digit = (10 - (total % 10)) % 10
        digits.append(check_digit)
        return "".join(map(str, digits))

    @staticmethod
    def is_luhn_valid(card_number: str) -> bool:
        """Validates whether a 16-digit card number passes the Luhn checksum check."""
        digits = [int(d) for d in card_number if d.isdigit()]
        if len(digits) != 16:
            return False
        total = 0
        for idx, digit in enumerate(reversed(digits)):
            if idx % 2 == 1:
                doubled = digit * 2
                total += doubled - 9 if doubled > 9 else doubled
            else:
                total += digit
        return total % 10 == 0

    @staticmethod
    def _generate_masked_card_number() -> str:
        pan = CardService.generate_luhn_pan()
        return f"**** **** **** {pan[-4:]}"

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
    async def get_user_cards(db: AsyncSession, user: User) -> list[CardResponse]:
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
