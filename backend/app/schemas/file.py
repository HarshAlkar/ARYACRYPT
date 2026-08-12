import uuid
from datetime import datetime
from pydantic import BaseModel

class FileBase(BaseModel):
    original_name: str
    mime_type: str
    size_bytes: int

class FileRead(FileBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}
