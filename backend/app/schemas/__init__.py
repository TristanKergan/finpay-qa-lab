from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# Auth Schemas
class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    full_name: str = Field(..., min_length=2, max_length=100)
    phone: str | None = Field(None, max_length=50)


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    full_name: str
    status: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6, max_length=100)


class PasswordResetSimulationRequest(BaseModel):
    email: EmailStr
    new_password: str = Field(..., min_length=6, max_length=100)


class UserResponse(BaseSchema):
    id: str
    email: str
    full_name: str
    phone: str | None = None
    avatar_url: str | None = None
    status: str
    created_at: datetime


class UserUpdateRequest(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    avatar_url: str | None = None


# Wallet Schemas
class WalletResponse(BaseSchema):
    id: str
    user_id: str
    currency: str
    balance: float
    available_balance: float
    created_at: datetime
    updated_at: datetime


class WalletSummaryResponse(BaseModel):
    wallets: list[WalletResponse]
    total_balance_usd: float


# Card Schemas
class CardCreateRequest(BaseModel):
    cardholder_name: str = Field(..., min_length=2, max_length=100)
    card_type: str = Field(default="VIRTUAL", pattern="^(DEBIT|CREDIT|VIRTUAL)$")
    spending_limit: float = Field(default=1000.0, gt=0)


class CardResponse(BaseSchema):
    id: str
    user_id: str
    card_number_masked: str
    cardholder_name: str
    expiry_date: str
    card_type: str
    status: str
    spending_limit: float
    created_at: datetime


class CardStatusUpdateRequest(BaseModel):
    status: str = Field(..., pattern="^(ACTIVE|FROZEN)$")


# Transfer Schemas
class TransferCreateRequest(BaseModel):
    receiver_email: EmailStr
    currency: str = Field(..., pattern="^(USD|EUR|UAH)$")
    amount: float
    description: str | None = Field(None, max_length=500)
    idempotency_key: str | None = Field(None, max_length=100)


class TransferResponse(BaseModel):
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


# Transaction Schemas
class TransactionResponse(BaseSchema):
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


class TransactionListResponse(BaseModel):
    items: list[TransactionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# Notification Schemas
class NotificationResponse(BaseSchema):
    id: str
    user_id: str
    type: str
    title: str
    message: str
    is_read: bool
    created_at: datetime


class NotificationListResponse(BaseModel):
    items: list[NotificationResponse]
    unread_count: int


# Webhook & Mock Provider Schemas
class MockPaymentProcessRequest(BaseModel):
    transaction_id: str
    amount: float
    currency: str = "USD"
    scenario: str = Field(default="SUCCESS", pattern="^(SUCCESS|FAILED|TIMEOUT|DUPLICATE)$")


class MockPaymentProcessResponse(BaseModel):
    status: str
    event_id: str
    transaction_id: str
    message: str


class PaymentWebhookPayload(BaseModel):
    event_id: str
    transaction_id: str
    status: str = Field(..., pattern="^(SUCCESS|FAILED)$")
    signature: str
    timestamp: str
