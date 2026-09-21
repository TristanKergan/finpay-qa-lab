from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import settings
from backend.app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)
from backend.app.models import Notification, RefreshToken, User, Wallet
from backend.app.schemas import (
    PasswordChangeRequest,
    PasswordResetSimulationRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
)


class AuthService:
    @staticmethod
    async def register(db: AsyncSession, req: UserRegisterRequest) -> User:
        # Check existing user
        result = await db.execute(select(User).where(User.email == req.email.lower()))
        existing = result.scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )

        # Create user
        user = User(
            email=req.email.lower(),
            hashed_password=get_password_hash(req.password),
            full_name=req.full_name,
            phone=req.phone,
            status="ACTIVE",
        )
        db.add(user)
        await db.flush()

        # Create default wallets (USD, EUR, UAH) with initial starting funds
        wallets = [
            Wallet(user_id=user.id, currency="USD", balance=1000.0, available_balance=1000.0),
            Wallet(user_id=user.id, currency="EUR", balance=500.0, available_balance=500.0),
            Wallet(user_id=user.id, currency="UAH", balance=10000.0, available_balance=10000.0),
        ]
        db.add_all(wallets)

        # Create welcome notification
        welcome_note = Notification(
            user_id=user.id,
            type="WELCOME",
            title="Welcome to FinPay!",
            message="Your account has been created with demo wallets in USD, EUR, and UAH."
        )
        db.add(welcome_note)

        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def login(db: AsyncSession, req: UserLoginRequest) -> TokenResponse:
        result = await db.execute(select(User).where(User.email == req.email.lower()))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        if user.status == "DELETED":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account has been deleted"
            )

        # Check account lock (BUG-009 check)
        is_bug_009 = settings.is_bug_active("009_LOCKED_USER_CAN_LOGIN")
        if user.status == "LOCKED" and not is_bug_009:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is locked due to security policy or excessive failed login attempts"
            )

        # Password validation
        if not verify_password(req.password, user.hashed_password):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= settings.MAX_FAILED_LOGIN_ATTEMPTS:
                user.status = "LOCKED"
                lock_note = Notification(
                    user_id=user.id,
                    type="ACCOUNT_LOCKED",
                    title="Security Alert: Account Locked",
                    message="Your account has been locked after multiple consecutive failed login attempts."
                )
                db.add(lock_note)
                await db.commit()
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Account is locked due to excessive failed login attempts"
                )
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Reset failed attempts
        user.failed_login_attempts = 0

        # Generate tokens
        access_token = create_access_token(
            subject=user.id,
            extra_claims={"email": user.email, "role": "user"}
        )
        raw_refresh, token_hash, expires_at = create_refresh_token(user.id)

        # Save refresh token in DB
        rf = RefreshToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
            revoked=False
        )
        db.add(rf)
        await db.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=raw_refresh,
            user_id=user.id,
            email=user.email,
            full_name=user.full_name,
            status=user.status
        )

    @staticmethod
    async def refresh_tokens(db: AsyncSession, refresh_token_str: str) -> TokenResponse:
        import hashlib
        token_hash = hashlib.sha256(refresh_token_str.encode("utf-8")).hexdigest()

        result = await db.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.revoked == False
            )
        )
        rf = result.scalar_one_or_none()
        if not rf:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or revoked refresh token"
            )

        # Check expiry
        now = datetime.now(timezone.utc)
        if rf.expires_at.tzinfo is None:
            rf_exp = rf.expires_at.replace(tzinfo=timezone.utc)
        else:
            rf_exp = rf.expires_at

        if rf_exp < now:
            rf.revoked = True
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired"
            )

        # Rotate refresh token
        rf.revoked = True

        user_res = await db.execute(select(User).where(User.id == rf.user_id))
        user = user_res.scalar_one_or_none()
        if not user or user.status != "ACTIVE":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive or not found"
            )

        # Generate new pair
        new_access = create_access_token(
            subject=user.id,
            extra_claims={"email": user.email, "role": "user"}
        )
        new_raw_refresh, new_hash, new_exp = create_refresh_token(user.id)

        new_rf = RefreshToken(
            user_id=user.id,
            token_hash=new_hash,
            expires_at=new_exp,
            revoked=False
        )
        db.add(new_rf)
        await db.commit()

        return TokenResponse(
            access_token=new_access,
            refresh_token=new_raw_refresh,
            user_id=user.id,
            email=user.email,
            full_name=user.full_name,
            status=user.status
        )

    @staticmethod
    async def logout(db: AsyncSession, refresh_token_str: str | None = None):
        if not refresh_token_str:
            return
        import hashlib
        token_hash = hashlib.sha256(refresh_token_str.encode("utf-8")).hexdigest()
        result = await db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        rf = result.scalar_one_or_none()
        if rf:
            rf.revoked = True
            await db.commit()

    @staticmethod
    async def change_password(db: AsyncSession, user: User, req: PasswordChangeRequest):
        if not verify_password(req.old_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect current password"
            )
        user.hashed_password = get_password_hash(req.new_password)
        await db.commit()

    @staticmethod
    async def reset_password_simulation(db: AsyncSession, req: PasswordResetSimulationRequest):
        result = await db.execute(select(User).where(User.email == req.email.lower()))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User with this email not found"
            )
        user.hashed_password = get_password_hash(req.new_password)
        user.failed_login_attempts = 0
        if user.status == "LOCKED":
            user.status = "ACTIVE"
        await db.commit()
