from datetime import datetime

from pydantic import BaseModel, EmailStr


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user_id: str
    email: EmailStr
    full_name: str
    status: str


class UserSchema(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    phone: str | None = None
    avatar_url: str | None = None
    status: str
    created_at: datetime


class WalletItemSchema(BaseModel):
    id: str
    user_id: str
    currency: str
    balance: float
    available_balance: float
    created_at: datetime
    updated_at: datetime


class WalletSummarySchema(BaseModel):
    wallets: list[WalletItemSchema]
    total_balance_usd: float


class TransferSchema(BaseModel):
    transaction_id: str
    status: str
    sender_email: str
    receiver_email: str
    amount: float
    currency: str
    converted_amount: float
    target_currency: str
    exchange_rate: float
    idempotency_key: str | None = None
    created_at: datetime
    message: str
    suppress_refresh: bool = False


class TransactionItemSchema(BaseModel):
    id: str
    sender_id: str | None = None
    receiver_id: str | None = None
    sender_email: str | None = None
    receiver_email: str | None = None
    amount: float
    currency: str
    converted_amount: float
    target_currency: str
    exchange_rate: float
    status: str
    idempotency_key: str | None = None
    description: str | None = None
    created_at: datetime
    completed_at: datetime | None = None


class TransactionListSchema(BaseModel):
    items: list[TransactionItemSchema]
    total: int
    page: int
    page_size: int
    total_pages: int


class CardSchema(BaseModel):
    id: str
    user_id: str
    card_number_masked: str
    cardholder_name: str
    expiry_date: str
    card_type: str
    status: str
    spending_limit: float
    created_at: datetime


class NotificationSchema(BaseModel):
    id: str
    user_id: str
    type: str
    title: str
    message: str
    is_read: bool
    created_at: datetime


class NotificationListSchema(BaseModel):
    items: list[NotificationSchema]
    unread_count: int
