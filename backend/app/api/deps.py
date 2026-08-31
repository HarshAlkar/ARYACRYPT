from typing import Generator
from uuid import UUID
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.core.config import settings
from app.core.exceptions import UnauthorizedException
from app.core.security import TOKEN_TYPE_ACCESS

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """Require a JWT access token. Refresh tokens are rejected."""
    from app.models.user import User

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        token_type = payload.get("type")
        if user_id is None:
            raise UnauthorizedException(detail="Could not validate credentials")
        if token_type != TOKEN_TYPE_ACCESS:
            raise UnauthorizedException(detail="Invalid access token")
        try:
            user_uuid = UUID(str(user_id))
        except (ValueError, TypeError):
            raise UnauthorizedException(detail="Could not validate credentials")
        token_version = int(payload.get("tv", 0))
    except JWTError:
        raise UnauthorizedException(detail="Could not validate credentials")

    user = db.query(User).filter(User.id == user_uuid).first()
    if not user:
        raise UnauthorizedException(detail="User not found")
    if not user.is_active:
        raise UnauthorizedException(detail="Inactive user")
    if getattr(user, "token_version", 0) != token_version:
        raise UnauthorizedException(detail="Session has been revoked")
    return user
