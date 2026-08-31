from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, PasswordChange
from app.core.security import get_password_hash, verify_password
from app.core.exceptions import BadRequestException, UnauthorizedException


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id) -> User | None:
    from uuid import UUID
    try:
        uid = user_id if isinstance(user_id, UUID) else UUID(str(user_id))
    except (ValueError, TypeError):
        return None
    return db.query(User).filter(User.id == uid).first()


def create_user(db: Session, user_in: UserCreate) -> User:
    db_user = User(
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        token_version=0,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def update_user_email(db: Session, user: User, user_in: UserUpdate) -> User:
    existing = get_user_by_email(db, email=user_in.email)
    if existing and existing.id != user.id:
        raise BadRequestException("Email is already in use")
    user.email = user_in.email
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def change_password(db: Session, user: User, body: PasswordChange) -> None:
    if not verify_password(body.current_password, user.password_hash):
        raise UnauthorizedException("Current password is incorrect")
    if body.current_password == body.new_password:
        raise BadRequestException("New password must be different from the current password")
    user.password_hash = get_password_hash(body.new_password)
    # Invalidate all existing access/refresh tokens for this user
    user.token_version = int(getattr(user, "token_version", 0) or 0) + 1
    db.add(user)
    db.commit()
