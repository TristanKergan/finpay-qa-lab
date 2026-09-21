import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


def get_uuid() -> str:
    return str(uuid.uuid4())


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=get_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    status = Column(String(20), default="ACTIVE", nullable=False)  # ACTIVE, LOCKED, DELETED
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)

    # Relationships
    wallets = relationship("Wallet", back_populates="user", cascade="all, delete-orphan")
    cards = relationship("Card", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")


class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(String(36), primary_key=True, default=get_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    currency = Column(String(10), nullable=False)  # USD, EUR, UAH
    balance = Column(Float, default=0.0, nullable=False)
    available_balance = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "currency", name="uq_user_currency"),
        Index("idx_wallet_user_currency", "user_id", "currency"),
    )

    user = relationship("User", back_populates="wallets")


class Card(Base):
    __tablename__ = "cards"

    id = Column(String(36), primary_key=True, default=get_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    card_number_masked = Column(String(30), nullable=False)  # e.g., **** **** **** 4123
    cardholder_name = Column(String(255), nullable=False)
    expiry_date = Column(String(10), nullable=False)  # MM/YY
    card_type = Column(String(20), default="DEBIT", nullable=False)  # DEBIT, CREDIT, VIRTUAL
    status = Column(String(20), default="ACTIVE", nullable=False)  # ACTIVE, FROZEN, DELETED
    spending_limit = Column(Float, default=1000.0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    user = relationship("User", back_populates="cards")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String(36), primary_key=True, default=get_uuid)
    sender_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    receiver_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    sender_wallet_id = Column(String(36), ForeignKey("wallets.id", ondelete="SET NULL"), nullable=True)
    receiver_wallet_id = Column(String(36), ForeignKey("wallets.id", ondelete="SET NULL"), nullable=True)
    
    amount = Column(Float, nullable=False)
    currency = Column(String(10), nullable=False)
    converted_amount = Column(Float, nullable=False)
    target_currency = Column(String(10), nullable=False)
    exchange_rate = Column(Float, default=1.0, nullable=False)
    
    status = Column(String(20), default="PENDING", nullable=False, index=True)  # PENDING, PROCESSING, SUCCESS, FAILED, CANCELLED
    idempotency_key = Column(String(100), nullable=True, unique=True, index=True)
    description = Column(String(500), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False, index=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=get_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(50), nullable=False)  # TRANSFER_SUCCESS, TRANSFER_FAILED, TRANSFER_INCOMING, CARD_FROZEN, ACCOUNT_LOCKED
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False, index=True)

    user = relationship("User", back_populates="notifications")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(String(36), primary_key=True, default=get_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(128), nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    user = relationship("User", back_populates="refresh_tokens")


class ProcessedWebhook(Base):
    __tablename__ = "processed_webhooks"

    id = Column(String(36), primary_key=True, default=get_uuid)
    event_id = Column(String(100), unique=True, nullable=False, index=True)
    transaction_id = Column(String(36), nullable=False, index=True)
    status = Column(String(50), nullable=False)
    payload_hash = Column(String(128), nullable=True)
    processed_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
