import uuid
from sqlalchemy import Column, String, BigInteger, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class CryptoActivity(Base):
    """Audit log for encrypt/decrypt operations used by dashboard & analytics."""

    __tablename__ = "crypto_activities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    file_id = Column(UUID(as_uuid=True), ForeignKey("files.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String, nullable=False)  # encrypt | decrypt
    status = Column(String, nullable=False)  # success | failure
    original_name = Column(String, nullable=True)
    file_size_bytes = Column(BigInteger, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    user = relationship("User", back_populates="activities")
