from datetime import timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.user import UserCreate, UserRead, UserLogin
from app.schemas.token import Token
from app.services import user_service
from app.core import security
from app.core.exceptions import BadRequestException, UnauthorizedException
from jose import jwt, JWTError
from app.core.config import settings

router = APIRouter()

@router.post("/register", response_model=UserRead)
def register(user_in: UserCreate, db: Session = Depends(deps.get_db)):
    """
    Register a new user.
    """
    user = user_service.get_user_by_email(db, email=user_in.email)
    if user:
        raise BadRequestException("User with this email already exists")
    
    new_user = user_service.create_user(db, user_in)
    return new_user

@router.post("/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(deps.get_db)):
    """
    Authenticate a user and return access & refresh tokens.
    """
    user = user_service.authenticate(db, email=user_in.email, password=user_in.password)
    if not user:
        raise UnauthorizedException("Incorrect email or password")
    if not user.is_active:
        raise UnauthorizedException("Inactive user")

    access_token = security.create_access_token(user.id)
    refresh_token = security.create_refresh_token(user.id)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=Token)
def refresh_token(refresh_token: str):
    """
    Refresh an access token using a valid refresh token.
    """
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        token_type = payload.get("type")
        if user_id is None or token_type != "refresh":
            raise UnauthorizedException("Invalid refresh token")
    except JWTError:
        raise UnauthorizedException("Could not validate refresh token")

    # Issue new access and refresh tokens
    new_access_token = security.create_access_token(user_id)
    new_refresh_token = security.create_refresh_token(user_id)
    
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserRead)
def get_current_user_profile(current_user = Depends(deps.get_current_user)):
    """
    Get the profile of the currently authenticated user.
    """
    return current_user

@router.post("/logout")
def logout():
    """
    Logout the user.
    Note: In a stateless JWT setup, this tells the client to destroy the token.
    For server-side invalidation, a Redis blacklist should be implemented here.
    """
    return {"message": "Successfully logged out. Please destroy tokens on the client side."}
