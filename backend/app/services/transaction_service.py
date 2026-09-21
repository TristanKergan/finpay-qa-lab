
from fastapi import HTTPException, status
from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import settings
from backend.app.models import Transaction, User
from backend.app.schemas import TransactionListResponse, TransactionResponse


class TransactionService:
    @staticmethod
    async def get_transactions(
        db: AsyncSession,
        user: User,
        page: int = 1,
        page_size: int = 10,
        status_filter: str | None = None,
        currency_filter: str | None = None,
        sort_by: str = "created_at",
        order: str = "desc"
    ) -> TransactionListResponse:
        # Base query: user is either sender or receiver
        base_query = select(Transaction).where(
            or_(Transaction.sender_id == user.id, Transaction.receiver_id == user.id)
        )

        if status_filter:
            base_query = base_query.where(Transaction.status == status_filter.upper())
        if currency_filter:
            base_query = base_query.where(Transaction.currency == currency_filter.upper())

        # Count query
        count_query = select(func.count()).select_from(base_query.subquery())
        total_count_res = await db.execute(count_query)
        total = total_count_res.scalar() or 0

        # Sorting
        sort_column = getattr(Transaction, sort_by, Transaction.created_at)
        order_func = desc if order.lower() == "desc" else asc
        ordered_query = base_query.order_by(order_func(sort_column))

        # Pagination & BUG-005 check
        is_bug_005 = settings.is_bug_active("005_PAGINATION_DUPLICATES")
        if is_bug_005 and page > 1:
            # Buggy offset reproduces duplicate records between consecutive pages
            offset_val = max(0, (page - 1) * page_size - 1)
        else:
            offset_val = (page - 1) * page_size

        paginated_query = ordered_query.offset(offset_val).limit(page_size)
        result = await db.execute(paginated_query)
        transactions = result.scalars().all()

        # Resolve sender & receiver emails
        items = []
        for txn in transactions:
            sender_email = None
            receiver_email = None
            if txn.sender_id:
                s_res = await db.execute(select(User.email).where(User.id == txn.sender_id))
                sender_email = s_res.scalar_one_or_none()
            if txn.receiver_id:
                r_res = await db.execute(select(User.email).where(User.id == txn.receiver_id))
                receiver_email = r_res.scalar_one_or_none()

            item = TransactionResponse(
                id=txn.id,
                sender_id=txn.sender_id,
                receiver_id=txn.receiver_id,
                sender_email=sender_email,
                receiver_email=receiver_email,
                amount=txn.amount,
                currency=txn.currency,
                converted_amount=txn.converted_amount,
                target_currency=txn.target_currency,
                exchange_rate=txn.exchange_rate,
                status=txn.status,
                idempotency_key=txn.idempotency_key,
                description=txn.description,
                created_at=txn.created_at,
                completed_at=txn.completed_at,
            )
            items.append(item)

        total_pages = max(1, (total + page_size - 1) // page_size) if page_size > 0 else 1

        return TransactionListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )

    @staticmethod
    async def get_transaction_by_id(
        db: AsyncSession,
        user: User,
        transaction_id: str
    ) -> TransactionResponse:
        res = await db.execute(select(Transaction).where(Transaction.id == transaction_id))
        txn = res.scalar_one_or_none()
        if not txn:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )

        # IDOR check: user must be sender or receiver
        if txn.sender_id != user.id and txn.receiver_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to view this transaction"
            )

        sender_email = None
        receiver_email = None
        if txn.sender_id:
            s_res = await db.execute(select(User.email).where(User.id == txn.sender_id))
            sender_email = s_res.scalar_one_or_none()
        if txn.receiver_id:
            r_res = await db.execute(select(User.email).where(User.id == txn.receiver_id))
            receiver_email = r_res.scalar_one_or_none()

        return TransactionResponse(
            id=txn.id,
            sender_id=txn.sender_id,
            receiver_id=txn.receiver_id,
            sender_email=sender_email,
            receiver_email=receiver_email,
            amount=txn.amount,
            currency=txn.currency,
            converted_amount=txn.converted_amount,
            target_currency=txn.target_currency,
            exchange_rate=txn.exchange_rate,
            status=txn.status,
            idempotency_key=txn.idempotency_key,
            description=txn.description,
            created_at=txn.created_at,
            completed_at=txn.completed_at,
        )
