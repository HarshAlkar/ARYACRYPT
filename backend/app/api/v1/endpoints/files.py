import os
import shutil
import uuid
import base64
import time
from pathlib import Path
from typing import Any, BinaryIO, List
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Response, UploadFile, File, Form, BackgroundTasks, Request
from fastapi.responses import FileResponse
from sqlalchemy import func
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict

# Dependency Injection for DB & Auth
from app.api import deps
from app.models.user import User
from app.models.file import File as DBFile
from app.models.activity import CryptoActivity
from app.core.config import settings
from app.core.logging import logger
from app.services.activity_service import log_activity
from app.schemas.file import (
    VaultStats,
    ActivityItem,
    DailyMetric,
    ProcessingPoint,
    SuccessRate,
    TrendPct,
)

# Cryptography via official AryaCrypt Python SDK (spec v1.1.0)
from aryacrypt import aes_gcm as arya_aes
from aryacrypt import format as arya_format
from aryacrypt import kdf as arya_kdf
from aryacrypt import preprocess as arya_preprocess
from aryacrypt.constants import (
    ALGORITHM_ID,
    MIN_PASSWORD_LENGTH,
    NONCE_LENGTH_BYTES,
    SALT_LENGTH_BYTES,
)
from aryacrypt.errors import AuthenticationError as AryaAuthError
from aryacrypt.errors import AryaCryptError, FormatError as AryaFormatError


router = APIRouter()

HISTORY_LIMIT_MAX = 100
MAX_UPLOAD_SIZE = settings.MAX_UPLOAD_SIZE_BYTES


class UploadTooLarge(Exception):
    """Raised when streamed upload bytes exceed MAX_UPLOAD_SIZE."""


class LimitedReader:
    """Wrap a binary stream and reject reads past ``max_bytes``."""

    def __init__(self, stream: BinaryIO, max_bytes: int) -> None:
        self._stream = stream
        self._max_bytes = max_bytes
        self._bytes_read = 0

    def read(self, size: int = -1) -> bytes:
        data = self._stream.read(size)
        if data:
            self._bytes_read += len(data)
            if self._bytes_read > self._max_bytes:
                raise UploadTooLarge()
        return data


def _enforce_content_length(request: Request) -> None:
    """Reject early when Content-Length alone already exceeds the upload cap."""
    raw = request.headers.get("content-length")
    if raw is None:
        return
    try:
        length = int(raw)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid Content-Length header.")
    if length > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Upload exceeds maximum allowed size.",
        )


def _resolve_under_upload_dir(storage_path: str | Path) -> Path:
    """
    Resolve ``storage_path`` and ensure it stays under UPLOAD_DIR (M5).
    Prevents path-traversal via crafted DB storage_path values.
    """
    upload_root = Path(settings.UPLOAD_DIR).resolve()
    resolved = Path(storage_path).resolve()
    try:
        resolved.relative_to(upload_root)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid storage path.")
    return resolved


def _user_vault_bytes_used(db: Session, user_id: UUID) -> int:
    total = (
        db.query(func.coalesce(func.sum(DBFile.file_size_bytes), 0))
        .filter(DBFile.user_id == user_id)
        .scalar()
    )
    return int(total or 0)


def _derive_key_from_password(
    password: str,
    salt: bytes,
    *,
    use_aryabhata: bool = True,
) -> bytes:
    """
    Derive AES-256 key via AryaCrypt SDK.

    New files: password → Aryabhata Base-100 diffusion → PBKDF2
    Legacy files: password UTF-8 bytes → PBKDF2 (pre-Aryabhata vault)

    Never logs key material, salt, password, or derived key bytes.
    """
    if use_aryabhata:
        _, key_material, _, _ = arya_preprocess.transform_password(password)
    else:
        key_material = password.encode("utf-8")

    return arya_kdf.derive_key(key_material, salt)


# ---------------------------------------------------------
# Pydantic Response DTOs
# ---------------------------------------------------------
class FileResponseDTO(BaseModel):
    """
    Data Transfer Object to safely serialize file metadata to the client 
    without exposing internal storage paths or sensitive backend structures.
    """
    id: UUID
    original_name: str
    encrypted_name: str
    file_size_bytes: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------
# Endpoints
# ---------------------------------------------------------
@router.post("/encrypt", response_model=FileResponseDTO)
def encrypt_and_store_file(
    request: Request,
    file: UploadFile = File(...),
    password: str = Form(...),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Receives an uploaded file and a password, applies Aryabhata Base-100
    preprocessing, then stream-encrypts with PBKDF2 + AES-256-GCM.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    if len(password) < MIN_PASSWORD_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Password must be at least {MIN_PASSWORD_LENGTH} characters for Aryabhata preprocessing.",
        )

    _enforce_content_length(request)

    started = time.perf_counter()
    file_id = uuid.uuid4()
    temp_storage_path: Path | None = None
    final_storage_path: Path | None = None

    try:
        logger.info(
            "encrypt start user_id=%s file_id=%s algorithm=%s",
            current_user.id,
            file_id,
            ALGORITHM_ID,
        )

        salt = os.urandom(SALT_LENGTH_BYTES)
        nonce = os.urandom(NONCE_LENGTH_BYTES)
        key = _derive_key_from_password(password, salt, use_aryabhata=True)

        storage_dir = Path(settings.UPLOAD_DIR)
        storage_dir.mkdir(parents=True, exist_ok=True)

        encrypted_name = f"{file.filename}.arya"
        final_storage_path = storage_dir / f"{current_user.id}_{file_id}.arya"
        temp_storage_path = storage_dir / f"temp_{file_id}.enc"

        limited_in = LimitedReader(file.file, MAX_UPLOAD_SIZE)
        with open(temp_storage_path, "wb") as temp_out:
            tag = arya_aes.encrypt_stream(key, nonce, limited_in, temp_out)

        metadata = arya_format.build_metadata(salt, nonce, tag)
        header_bytes = arya_format.serialize_header(metadata)

        with open(final_storage_path, "wb") as final_out:
            final_out.write(header_bytes)
            with open(temp_storage_path, "rb") as temp_in:
                shutil.copyfileobj(temp_in, final_out)

        temp_storage_path.unlink(missing_ok=True)
        temp_storage_path = None

        file_size = final_storage_path.stat().st_size
        duration_ms = int((time.perf_counter() - started) * 1000)

        # M7: vault capacity before completing encrypt
        used = _user_vault_bytes_used(db, current_user.id)
        if used + file_size > settings.VAULT_CAPACITY_BYTES:
            final_storage_path.unlink(missing_ok=True)
            final_storage_path = None
            logger.info(
                "encrypt failure user_id=%s file_id=%s algorithm=%s reason=vault_capacity duration_ms=%s",
                current_user.id,
                file_id,
                ALGORITHM_ID,
                duration_ms,
            )
            raise HTTPException(
                status_code=413,
                detail="Vault capacity exceeded.",
            )

        db_file = DBFile(
            id=file_id,
            user_id=current_user.id,
            original_name=file.filename,
            encrypted_name=encrypted_name,
            file_size_bytes=file_size,
            storage_path=str(final_storage_path)
        )
        db.add(db_file)
        db.flush()
        log_activity(
            db,
            user_id=current_user.id,
            action="encrypt",
            status="success",
            file_id=file_id,
            original_name=file.filename,
            file_size_bytes=file_size,
            duration_ms=duration_ms,
            commit=False,
        )
        try:
            db.commit()
        except Exception:
            db.rollback()
            # M6: unlink final .arya if DB commit fails after write
            if final_storage_path is not None and final_storage_path.exists():
                final_storage_path.unlink(missing_ok=True)
            logger.error(
                "encrypt failure user_id=%s file_id=%s algorithm=%s reason=db_commit duration_ms=%s",
                current_user.id,
                file_id,
                ALGORITHM_ID,
                duration_ms,
            )
            raise HTTPException(status_code=500, detail="Encryption failed")
        db.refresh(db_file)

        logger.info(
            "encrypt success user_id=%s file_id=%s algorithm=%s duration_ms=%s",
            current_user.id,
            file_id,
            ALGORITHM_ID,
            duration_ms,
        )
        return db_file

    except HTTPException:
        raise
    except UploadTooLarge:
        if temp_storage_path is not None and temp_storage_path.exists():
            temp_storage_path.unlink(missing_ok=True)
        if final_storage_path is not None and final_storage_path.exists():
            final_storage_path.unlink(missing_ok=True)
        logger.info(
            "encrypt failure user_id=%s file_id=%s algorithm=%s reason=upload_too_large",
            current_user.id,
            file_id,
            ALGORITHM_ID,
        )
        raise HTTPException(
            status_code=413,
            detail="Upload exceeds maximum allowed size.",
        )
    except (ValueError, TypeError, OverflowError, AryaCryptError) as e:
        if temp_storage_path is not None and temp_storage_path.exists():
            temp_storage_path.unlink(missing_ok=True)
        if final_storage_path is not None and final_storage_path.exists():
            final_storage_path.unlink(missing_ok=True)
        logger.info(
            "encrypt failure user_id=%s file_id=%s algorithm=%s reason=validation",
            current_user.id,
            file_id,
            ALGORITHM_ID,
        )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        if temp_storage_path is not None and temp_storage_path.exists():
            temp_storage_path.unlink(missing_ok=True)
        if final_storage_path is not None and final_storage_path.exists():
            final_storage_path.unlink(missing_ok=True)
        logger.error(
            "encrypt failure user_id=%s file_id=%s algorithm=%s",
            current_user.id,
            file_id,
            ALGORITHM_ID,
        )
        raise HTTPException(status_code=500, detail="Encryption failed")


def remove_file(path: Path):
    try:
        if path.exists():
            path.unlink()
    except Exception:
        pass


def _decrypt_arya_stream_to_temp(
    *,
    in_stream,
    password: str,
    source_label: str,
    user_id,
    storage_dir: Path,
) -> Path:
    """
    Shared decrypt core: parse ARYA header, Aryabhata/legacy KDF, AES-GCM verify.
    Returns path to a temp plaintext file.
    Uses try/finally so temp plaintext is removed on any failure (M4).
    """
    temp_id = uuid.uuid4()
    temp_decrypted_path = storage_dir / f"decrypted_{temp_id}.tmp"
    success = False
    algorithm = ALGORITHM_ID

    try:
        logger.info(
            "decrypt start user_id=%s source=%s",
            user_id,
            source_label,
        )

        metadata, _header_len = arya_format.deserialize_from_stream(in_stream)
        algorithm = metadata.get("algorithm", ALGORITHM_ID)
        use_aryabhata = arya_preprocess.uses_aryabhata(algorithm)

        salt = base64.b64decode(metadata["salt"])
        nonce = base64.b64decode(metadata["nonce"])
        auth_tag = base64.b64decode(metadata["auth_tag"])

        if use_aryabhata and len(password) < MIN_PASSWORD_LENGTH:
            raise HTTPException(
                status_code=400,
                detail=f"Password must be at least {MIN_PASSWORD_LENGTH} characters for Aryabhata preprocessing.",
            )

        key = _derive_key_from_password(
            password,
            salt,
            use_aryabhata=use_aryabhata,
        )

        with open(temp_decrypted_path, "wb") as temp_out:
            arya_aes.decrypt_stream(key, nonce, auth_tag, in_stream, temp_out)

        success = True
        logger.info(
            "decrypt success user_id=%s algorithm=%s",
            user_id,
            algorithm,
        )
        return temp_decrypted_path

    except HTTPException:
        logger.info(
            "decrypt failure user_id=%s algorithm=%s",
            user_id,
            algorithm,
        )
        raise
    except AryaFormatError as me:
        logger.info(
            "decrypt failure user_id=%s algorithm=%s reason=format",
            user_id,
            algorithm,
        )
        raise HTTPException(status_code=400, detail=f"Invalid file format: {str(me)}")
    except AryaAuthError:
        logger.info(
            "decrypt failure user_id=%s algorithm=%s reason=auth",
            user_id,
            algorithm,
        )
        raise HTTPException(
            status_code=401,
            detail="Authentication failed: Incorrect password or tampered file.",
        )
    except UploadTooLarge:
        logger.info(
            "decrypt failure user_id=%s algorithm=%s reason=upload_too_large",
            user_id,
            algorithm,
        )
        raise HTTPException(
            status_code=413,
            detail="Upload exceeds maximum allowed size.",
        )
    except (ValueError, TypeError, OverflowError, AryaCryptError) as e:
        logger.info(
            "decrypt failure user_id=%s algorithm=%s reason=validation",
            user_id,
            algorithm,
        )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.error(
            "decrypt failure user_id=%s algorithm=%s",
            user_id,
            algorithm,
        )
        raise HTTPException(status_code=500, detail="Decryption failed")
    finally:
        if not success and temp_decrypted_path.exists():
            try:
                temp_decrypted_path.unlink()
            except Exception:
                pass


@router.post("/decrypt")
def decrypt_file(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    password: str = Form(...),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Receives an uploaded .arya file and password, decrypts it to a temporary file 
    after strictly verifying the GCM Auth Tag, and returns the original file for download.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    _enforce_content_length(request)

    storage_dir = Path(settings.UPLOAD_DIR)
    storage_dir.mkdir(parents=True, exist_ok=True)

    started = time.perf_counter()
    original_filename = file.filename
    if original_filename.endswith(".arya"):
        original_filename = original_filename[:-5]

    limited_in = LimitedReader(file.file, MAX_UPLOAD_SIZE)

    try:
        temp_decrypted_path = _decrypt_arya_stream_to_temp(
            in_stream=limited_in,
            password=password,
            source_label=file.filename,
            user_id=current_user.id,
            storage_dir=storage_dir,
        )
    except HTTPException as exc:
        if exc.status_code in (401, 400, 413):
            log_activity(
                db,
                user_id=current_user.id,
                action="decrypt",
                status="failure",
                original_name=original_filename,
                duration_ms=int((time.perf_counter() - started) * 1000),
            )
        raise

    duration_ms = int((time.perf_counter() - started) * 1000)
    size_bytes = temp_decrypted_path.stat().st_size if temp_decrypted_path.exists() else None
    log_activity(
        db,
        user_id=current_user.id,
        action="decrypt",
        status="success",
        original_name=original_filename,
        file_size_bytes=size_bytes,
        duration_ms=duration_ms,
    )

    background_tasks.add_task(remove_file, temp_decrypted_path)

    return FileResponse(
        path=temp_decrypted_path,
        filename=original_filename,
        media_type="application/octet-stream"
    )


@router.post("/{file_id}/decrypt")
def decrypt_vault_file(
    file_id: str,
    background_tasks: BackgroundTasks,
    password: str = Form(...),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Decrypt a vault-stored .arya file in place (no client re-upload).
    Ownership is enforced via JWT.
    """
    try:
        uuid_obj = UUID(file_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid file ID format (must be UUID).")

    file_record = db.query(DBFile).filter(
        DBFile.id == uuid_obj,
        DBFile.user_id == current_user.id,
    ).first()
    if not file_record:
        raise HTTPException(status_code=404, detail="File record not found or access denied.")

    storage_path = _resolve_under_upload_dir(file_record.storage_path)
    if not storage_path.exists():
        raise HTTPException(status_code=404, detail="Encrypted file missing from vault storage.")

    storage_dir = Path(settings.UPLOAD_DIR)
    storage_dir.mkdir(parents=True, exist_ok=True)

    started = time.perf_counter()
    try:
        with open(storage_path, "rb") as in_stream:
            temp_decrypted_path = _decrypt_arya_stream_to_temp(
                in_stream=in_stream,
                password=password,
                source_label=f"vault:{file_id}",
                user_id=current_user.id,
                storage_dir=storage_dir,
            )
    except HTTPException as exc:
        if exc.status_code in (401, 400, 413):
            log_activity(
                db,
                user_id=current_user.id,
                action="decrypt",
                status="failure",
                file_id=file_record.id,
                original_name=file_record.original_name,
                file_size_bytes=file_record.file_size_bytes,
                duration_ms=int((time.perf_counter() - started) * 1000),
            )
        raise

    duration_ms = int((time.perf_counter() - started) * 1000)
    log_activity(
        db,
        user_id=current_user.id,
        action="decrypt",
        status="success",
        file_id=file_record.id,
        original_name=file_record.original_name,
        file_size_bytes=file_record.file_size_bytes,
        duration_ms=duration_ms,
    )

    background_tasks.add_task(remove_file, temp_decrypted_path)

    return FileResponse(
        path=temp_decrypted_path,
        filename=file_record.original_name,
        media_type="application/octet-stream",
    )


@router.get("/history", response_model=List[FileResponseDTO])
def get_encryption_history(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Retrieves the complete encryption/decryption history for the authenticated user.
    Results are automatically paginated and sorted by newest first.
    """
    if skip < 0:
        skip = 0
    limit = min(max(limit, 1), HISTORY_LIMIT_MAX)

    files = db.query(DBFile)\
              .filter(DBFile.user_id == current_user.id)\
              .order_by(DBFile.created_at.desc())\
              .offset(skip).limit(limit).all()
              
    return files


def _pct_change(current: int, previous: int) -> float:
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    return round(((current - previous) / previous) * 100.0, 1)


@router.get("/stats", response_model=VaultStats)
def get_vault_stats(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> VaultStats:
    """Aggregated vault metrics for dashboard and analytics (real audit data)."""
    files = (
        db.query(DBFile)
        .filter(DBFile.user_id == current_user.id)
        .order_by(DBFile.created_at.desc())
        .all()
    )
    activities = (
        db.query(CryptoActivity)
        .filter(CryptoActivity.user_id == current_user.id)
        .order_by(CryptoActivity.created_at.desc())
        .limit(1000)
        .all()
    )

    total_files = len(files)
    storage_used = sum(f.file_size_bytes or 0 for f in files)
    total_encrypted = sum(1 for a in activities if a.action == "encrypt" and a.status == "success")
    if total_encrypted == 0:
        total_encrypted = total_files
    total_decrypted = sum(1 for a in activities if a.action == "decrypt" and a.status == "success")
    security_alerts = sum(1 for a in activities if a.status == "failure")

    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)
    two_weeks_ago = now - timedelta(days=14)

    def _aware(dt: datetime | None) -> datetime | None:
        if dt is None:
            return None
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt

    files_this = sum(1 for f in files if (t := _aware(f.created_at)) and t >= week_ago)
    files_prev = sum(
        1 for f in files if (t := _aware(f.created_at)) and two_weeks_ago <= t < week_ago
    )
    enc_this = sum(
        1
        for a in activities
        if a.action == "encrypt"
        and a.status == "success"
        and (t := _aware(a.created_at))
        and t >= week_ago
    )
    enc_prev = sum(
        1
        for a in activities
        if a.action == "encrypt"
        and a.status == "success"
        and (t := _aware(a.created_at))
        and two_weeks_ago <= t < week_ago
    )
    dec_this = sum(
        1
        for a in activities
        if a.action == "decrypt"
        and a.status == "success"
        and (t := _aware(a.created_at))
        and t >= week_ago
    )
    dec_prev = sum(
        1
        for a in activities
        if a.action == "decrypt"
        and a.status == "success"
        and (t := _aware(a.created_at))
        and two_weeks_ago <= t < week_ago
    )

    # Daily buckets (last 7 days)
    day_meta: list[tuple[str, str]] = []  # (iso_key, label)
    volume_map: dict[str, float] = {}
    ops_count: dict[str, int] = {}
    ops_encrypt: dict[str, int] = {}
    ops_decrypt: dict[str, int] = {}
    for i in range(6, -1, -1):
        d = (now - timedelta(days=i)).date()
        key = d.isoformat()
        label = d.strftime("%b %d")
        day_meta.append((key, label))
        volume_map[key] = 0.0
        ops_count[key] = 0
        ops_encrypt[key] = 0
        ops_decrypt[key] = 0

    for f in files:
        t = _aware(f.created_at)
        if not t:
            continue
        key = t.date().isoformat()
        if key in volume_map:
            volume_map[key] += (f.file_size_bytes or 0) / (1024 * 1024)

    for a in activities:
        t = _aware(a.created_at)
        if not t:
            continue
        key = t.date().isoformat()
        if key not in ops_count or a.status != "success":
            continue
        ops_count[key] += 1
        if a.action == "encrypt":
            ops_encrypt[key] += 1
        elif a.action == "decrypt":
            ops_decrypt[key] += 1

    # Fallback: if no encrypt activities yet, derive frequency from files
    if sum(ops_encrypt.values()) == 0:
        for f in files:
            t = _aware(f.created_at)
            if not t:
                continue
            key = t.date().isoformat()
            if key in ops_count:
                ops_count[key] += 1
                ops_encrypt[key] += 1

    daily_volume = [
        DailyMetric(date=label, size_mb=round(volume_map[key], 3), count=0)
        for key, label in day_meta
    ]
    daily_ops = [
        DailyMetric(
            date=label,
            size_mb=0.0,
            count=ops_count[key],
            encrypt_count=ops_encrypt[key],
            decrypt_count=ops_decrypt[key],
        )
        for key, label in day_meta
    ]

    processing = [
        ProcessingPoint(
            size_mb=round((a.file_size_bytes or 0) / (1024 * 1024), 3),
            time_ms=a.duration_ms or 0,
            action=a.action,
        )
        for a in activities
        if a.status == "success" and a.duration_ms is not None
    ][:100]

    success_count = sum(1 for a in activities if a.status == "success")
    failure_count = sum(1 for a in activities if a.status == "failure")

    recent = [
        ActivityItem(
            id=a.id,
            action=a.action.capitalize(),
            status="Success" if a.status == "success" else "Failed",
            original_name=a.original_name,
            file_size_bytes=a.file_size_bytes,
            duration_ms=a.duration_ms,
            created_at=a.created_at,
        )
        for a in activities[:20]
    ]

    return VaultStats(
        total_files=total_files,
        total_encrypted=total_encrypted,
        total_decrypted=total_decrypted,
        security_alerts=security_alerts,
        storage_used_bytes=storage_used,
        storage_capacity_bytes=settings.VAULT_CAPACITY_BYTES,
        trends=TrendPct(
            files=_pct_change(files_this, files_prev),
            encrypt=_pct_change(enc_this, enc_prev),
            decrypt=_pct_change(dec_this, dec_prev),
        ),
        recent_activity=recent,
        daily_volume=daily_volume,
        daily_ops=daily_ops,
        processing=processing,
        success_rate=SuccessRate(success=success_count, failure=failure_count),
    )


@router.get("/{file_id}/download")
def download_encrypted_file(
    file_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Downloads the stored encrypted `.arya` file from the user's vault.
    Ownership is enforced via JWT; only the owner can download.
    """
    try:
        uuid_obj = UUID(file_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid file ID format (must be UUID).")

    file_record = db.query(DBFile).filter(
        DBFile.id == uuid_obj,
        DBFile.user_id == current_user.id
    ).first()

    if not file_record:
        raise HTTPException(status_code=404, detail="File record not found or access denied.")

    storage_path = _resolve_under_upload_dir(file_record.storage_path)
    if not storage_path.exists():
        raise HTTPException(status_code=404, detail="Encrypted file missing from vault storage.")

    logger.info(
        "download user_id=%s file_id=%s",
        current_user.id,
        file_id,
    )

    return FileResponse(
        path=storage_path,
        filename=file_record.encrypted_name,
        media_type="application/octet-stream",
    )


@router.get("/{file_id}", response_model=FileResponseDTO)
def get_file_metadata(
    file_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Retrieves the specific metadata for a single encrypted file record.
    Strictly verifies ownership against the current user's JWT.
    """
    try:
        uuid_obj = UUID(file_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid file ID format (must be UUID).")

    file_record = db.query(DBFile).filter(DBFile.id == uuid_obj, DBFile.user_id == current_user.id).first()
    
    if not file_record:
        raise HTTPException(status_code=404, detail="File record not found or access denied.")
        
    return file_record


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_file_record(
    file_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> None:
    """
    Permanently deletes a file from the user's AryaCrypt vault.
    This safely erases the encrypted `.arya` binary from the local disk 
    and cascades the deletion through the PostgreSQL database.
    """
    try:
        uuid_obj = UUID(file_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid file ID format.")

    # 1. Enforce Authorization
    file_record = db.query(DBFile).filter(DBFile.id == uuid_obj, DBFile.user_id == current_user.id).first()
    if not file_record:
        raise HTTPException(status_code=404, detail="File record not found or access denied.")
        
    # 2. Safely Erase Physical File (path must stay under UPLOAD_DIR)
    try:
        storage_path = _resolve_under_upload_dir(file_record.storage_path)
        if storage_path.exists():
            storage_path.unlink()
    except HTTPException:
        raise
    except Exception:
        logger.warning(
            "delete physical file failed user_id=%s file_id=%s",
            current_user.id,
            file_id,
        )
        
    # 3. Erase Database Record
    db.delete(file_record)
    db.commit()

    logger.info(
        "delete success user_id=%s file_id=%s",
        current_user.id,
        file_id,
    )
    
    return None
