import uuid
from sqlalchemy import Column, String, BigInteger, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class File(Base):
    __tablename__ = "files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    original_name = Column(String, nullable=False)
    encrypted_name = Column(String, nullable=True)
    file_size_bytes = Column(BigInteger, nullable=False)
    storage_path = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="files")
    
    # These will be uncommented or added later when their respective models are created
    # key_metadata = relationship("KeysMetadata", back_populates="file", uselist=False, cascade="all, delete-orphan")
    # encryption_logs = relationship("EncryptionLog", back_populates="file", cascade="all, delete-orphan")
