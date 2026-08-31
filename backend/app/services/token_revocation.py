"""Durable refresh-token revocation (DB-backed). Stores SHA-256 hashes only."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from uuid import UUID

from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.refresh_revocation import RefreshTokenRevocation


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _token_expiry(token: str) -> datetime | None:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": False},
        )
        exp = payload.get("exp")
        if exp is None:
            return None
        return datetime.fromtimestamp(int(exp), tz=timezone.utc)
    except JWTError:
        return None


def revoke_refresh_token(db: Session, token: str, user_id: UUID | None = None) -> None:
    if not token:
        return
    digest = hash_token(token)
    existing = (
        db.query(RefreshTokenRevocation)
        .filter(RefreshTokenRevocation.token_hash == digest)
        .first()
    )
    if existing:
        return
    expires_at = _token_expiry(token)
    if expires_at is None:
        # Unknown/malformed — still store short TTL so attackers cannot probe forever
        expires_at = datetime.now(timezone.utc)
    row = RefreshTokenRevocation(
        token_hash=digest,
        user_id=user_id,
        expires_at=expires_at,
    )
    db.add(row)
    db.commit()


def is_refresh_token_revoked(db: Session, token: str) -> bool:
    if not token:
        return True
    digest = hash_token(token)
    now = datetime.now(timezone.utc)
    row = (
        db.query(RefreshTokenRevocation)
        .filter(
            RefreshTokenRevocation.token_hash == digest,
            RefreshTokenRevocation.expires_at >= now,
        )
        .first()
    )
    return row is not None


def purge_expired_revocations(db: Session) -> int:
    now = datetime.now(timezone.utc)
    q = db.query(RefreshTokenRevocation).filter(RefreshTokenRevocation.expires_at < now)
    count = q.count()
    q.delete(synchronize_session=False)
    db.commit()
    return count
