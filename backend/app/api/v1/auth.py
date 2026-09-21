from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.deps import get_current_user
from backend.app.core.database import get_db
from backend.app.models import User
from backend.app.schemas import (
    PasswordChangeRequest,
    PasswordResetSimulationRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from backend.app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(req: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    user = await AuthService.register(db, req)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse)
async def login(req: UserLoginRequest, db: AsyncSession = Depends(get_db)):
    return await AuthService.login(db, req)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(req: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    return await AuthService.refresh_tokens(db, req.refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(req: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    await AuthService.logout(db, req.refresh_token)


@router.post("/password/change")
async def change_password(
    req: PasswordChangeRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await AuthService.change_password(db, user, req)
    return {"message": "Password changed successfully"}


@router.post("/password/reset")
async def reset_password(
    req: PasswordResetSimulationRequest,
    db: AsyncSession = Depends(get_db)
):
    await AuthService.reset_password_simulation(db, req)
    return {"message": "Password reset successfully"}
