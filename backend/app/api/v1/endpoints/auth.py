from fastapi import APIRouter, Body, Cookie, Depends, Response
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.api import deps
from app.schemas.user import (
    UserCreate,
    UserRead,
    UserLogin,
    UserUpdate,
    PasswordChange,
    RefreshTokenRequest,
    LogoutRequest,
)
from app.schemas.token import Token
from app.services import user_service
from app.services import token_revocation
from app.core import security
from app.core.exceptions import BadRequestException, UnauthorizedException
from app.core.security import TOKEN_TYPE_REFRESH
from app.core.config import settings

router = APIRouter()

REFRESH_COOKIE = "aryacrypt_refresh"
COOKIE_MAX_AGE = settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE,
        value=refresh_token,
        httponly=True,
        secure=settings.REFRESH_COOKIE_SECURE,
        samesite="lax",
        max_age=COOKIE_MAX_AGE,
        path="/api/v1/auth",
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(key=REFRESH_COOKIE, path="/api/v1/auth")


@router.post("/register", response_model=UserRead)
def register(user_in: UserCreate, db: Session = Depends(deps.get_db)):
    user = user_service.get_user_by_email(db, email=user_in.email)
    if user:
        raise BadRequestException("User with this email already exists")
    return user_service.create_user(db, user_in)


@router.post("/login", response_model=Token)
def login(
    user_in: UserLogin,
    response: Response,
    db: Session = Depends(deps.get_db),
):
    user = user_service.authenticate(db, email=user_in.email, password=user_in.password)
    if not user:
        raise UnauthorizedException("Incorrect email or password")
    if not user.is_active:
        raise UnauthorizedException("Inactive user")

    tv = getattr(user, "token_version", 0) or 0
    access_token = security.create_access_token(user.id, token_version=tv)
    refresh_token = security.create_refresh_token(user.id, token_version=tv)
    _set_refresh_cookie(response, refresh_token)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=Token)
def refresh_token_endpoint(
    response: Response,
    body: RefreshTokenRequest = Body(default_factory=RefreshTokenRequest),
    db: Session = Depends(deps.get_db),
    aryacrypt_refresh: str | None = Cookie(default=None),
):
    token = body.refresh_token or aryacrypt_refresh
    if not token:
        raise UnauthorizedException("Refresh token required")

    if token_revocation.is_refresh_token_revoked(db, token):
        raise UnauthorizedException("Refresh token has been revoked")

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        token_type = payload.get("type")
        if user_id is None or token_type != TOKEN_TYPE_REFRESH:
            raise UnauthorizedException("Invalid refresh token")
        token_version = int(payload.get("tv", 0))
    except JWTError:
        raise UnauthorizedException("Could not validate refresh token")

    user = user_service.get_user_by_id(db, user_id)
    if not user or not user.is_active:
        raise UnauthorizedException("User not found or inactive")
    if getattr(user, "token_version", 0) != token_version:
        raise UnauthorizedException("Session has been revoked")

    token_revocation.revoke_refresh_token(db, token, user_id=user.id)
    tv = getattr(user, "token_version", 0) or 0
    new_access = security.create_access_token(user.id, token_version=tv)
    new_refresh = security.create_refresh_token(user.id, token_version=tv)
    _set_refresh_cookie(response, new_refresh)
    return {
        "access_token": new_access,
        "refresh_token": new_refresh,
        "token_type": "bearer",
    }


@router.get("/me", response_model=UserRead)
def get_current_user_profile(current_user=Depends(deps.get_current_user)):
    return current_user


@router.patch("/me", response_model=UserRead)
def update_current_user_profile(
    user_in: UserUpdate,
    db: Session = Depends(deps.get_db),
    current_user=Depends(deps.get_current_user),
):
    return user_service.update_user_email(db, current_user, user_in)


@router.post("/change-password")
def change_password(
    body: PasswordChange,
    db: Session = Depends(deps.get_db),
    current_user=Depends(deps.get_current_user),
):
    user_service.change_password(db, current_user, body)
    return {"message": "Password updated successfully"}


@router.post("/logout")
def logout(
    response: Response,
    body: LogoutRequest = LogoutRequest(),
    db: Session = Depends(deps.get_db),
    aryacrypt_refresh: str | None = Cookie(default=None),
):
    token = body.refresh_token or aryacrypt_refresh
    if token:
        user_id = None
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
                options={"verify_exp": False},
            )
            from uuid import UUID

            user_id = UUID(str(payload.get("sub"))) if payload.get("sub") else None
        except Exception:
            user_id = None
        token_revocation.revoke_refresh_token(db, token, user_id=user_id)
    _clear_refresh_cookie(response)
    return {"message": "Successfully logged out"}
