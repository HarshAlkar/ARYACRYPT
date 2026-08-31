import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.base_class import Base


class RefreshTokenRevocation(Base):
    """Durable refresh-token denylist (stores SHA-256 of token, never raw JWT)."""

    __tablename__ = "refresh_token_revocations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    token_hash = Column(String(64), nullable=False, unique=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


Index("ix_refresh_revocations_hash_expires", RefreshTokenRevocation.token_hash, RefreshTokenRevocation.expires_at)
