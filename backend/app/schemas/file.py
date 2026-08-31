import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class FileRead(BaseModel):
    id: uuid.UUID
    original_name: str
    encrypted_name: str | None = None
    file_size_bytes: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ActivityItem(BaseModel):
    id: uuid.UUID
    action: str
    status: str
    original_name: str | None = None
    file_size_bytes: int | None = None
    duration_ms: int | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DailyMetric(BaseModel):
    date: str
    size_mb: float = 0.0
    count: int = 0
    encrypt_count: int = 0
    decrypt_count: int = 0


class ProcessingPoint(BaseModel):
    size_mb: float
    time_ms: int
    action: str


class SuccessRate(BaseModel):
    success: int
    failure: int


class TrendPct(BaseModel):
    files: float
    encrypt: float
    decrypt: float


class VaultStats(BaseModel):
    total_files: int
    total_encrypted: int
    total_decrypted: int
    security_alerts: int
    storage_used_bytes: int
    storage_capacity_bytes: int
    trends: TrendPct
    recent_activity: list[ActivityItem]
    daily_volume: list[DailyMetric]
    daily_ops: list[DailyMetric]
    processing: list[ProcessingPoint]
    success_rate: SuccessRate
