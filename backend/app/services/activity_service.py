"""Helpers for persisting crypto activity / audit events."""

from uuid import UUID
from sqlalchemy.orm import Session
from app.models.activity import CryptoActivity


def log_activity(
    db: Session,
    *,
    user_id: UUID,
    action: str,
    status: str,
    file_id: UUID | None = None,
    original_name: str | None = None,
    file_size_bytes: int | None = None,
    duration_ms: int | None = None,
    commit: bool = True,
) -> CryptoActivity:
    row = CryptoActivity(
        user_id=user_id,
        file_id=file_id,
        action=action,
        status=status,
        original_name=original_name,
        file_size_bytes=file_size_bytes,
        duration_ms=duration_ms,
    )
    db.add(row)
    if commit:
        db.commit()
        db.refresh(row)
    return row
