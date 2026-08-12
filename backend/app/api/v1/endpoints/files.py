import os
import shutil
import uuid
import base64
from pathlib import Path
from typing import Any, List
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Response, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict

# Dependency Injection for DB & Auth
from app.api import deps
from app.models.user import User
from app.models.file import File as DBFile
from app.core.config import settings
from app.core.logging import logger

# Cryptography
from app.crypto.salt import SaltManager
from app.crypto.nonce import NonceManager
from app.crypto.key_manager import KeyManager
from app.crypto.aes import AESManager, AESGCMDecryptionError
from app.crypto.metadata import EncryptedFileMetadata, MetadataError

# Aryabhata preprocessing (real AryaCrypt layer)
from app.framework.aryabhata.preprocess import AryabhataPreprocessor
from app.framework.aryabhata.constants import MIN_PASSWORD_LENGTH


router = APIRouter()
_preprocessor = AryabhataPreprocessor()


def _log_crypto_banner(title: str) -> None:
    logger.info("=" * 64)
    logger.info(title)
    logger.info("=" * 64)


def _derive_key_from_password(
    password: str,
    salt: bytes,
    *,
    use_aryabhata: bool = True,
    log: bool = True,
) -> bytes:
    """
    Derive AES-256 key.

    New files: password → Aryabhata Base-100 diffusion → PBKDF2
    Legacy files: password UTF-8 bytes → PBKDF2 (pre-Aryabhata vault)
    """
    if use_aryabhata:
        result = _preprocessor.transform(password, log=log)
        key_material = result.stream_bytes
    else:
        if log:
            logger.info("[LEGACY] Skipping Aryabhata — raw UTF-8 password -> PBKDF2")
        key_material = password.encode("utf-8")

    if log:
        logger.info("[KDF] PBKDF2-HMAC-SHA256 key derivation")
        logger.info(
            f"      iterations={KeyManager.DEFAULT_ITERATIONS:,}  "
            f"dklen={KeyManager.KEY_LENGTH_BYTES} bytes"
        )

    key = KeyManager.derive_key(key_material, salt)

    if log:
        logger.info(f"      key = {key.hex()[:16]}... (hidden; {len(key)} bytes / 256-bit)")

    return key


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

    try:
        _log_crypto_banner(f"[ENCRYPT] Starting for '{file.filename}' (user={current_user.id})")
        logger.info("Pipeline: Password -> Aryabhata(Base-100) -> PBKDF2 -> AES-256-GCM")

        # 1. Cryptographic Setup
        logger.info("[1/7] Generating CSPRNG salt (16 bytes, NIST SP 800-132)")
        salt = SaltManager.generate()
        logger.info(f"      salt  = {salt.hex()[:24]}... ({len(salt)} bytes)")

        logger.info("[2/7] Generating AES-GCM nonce (12 bytes, NIST SP 800-38D)")
        nonce = NonceManager.generate()
        logger.info(f"      nonce = {nonce.hex()} ({len(nonce)} bytes)")

        logger.info("[3/7] Aryabhata preprocessing + PBKDF2 key derivation")
        key = _derive_key_from_password(password, salt, use_aryabhata=True, log=True)
        
        # 2. Prepare Storage Paths
        storage_dir = Path(settings.UPLOAD_DIR)
        storage_dir.mkdir(parents=True, exist_ok=True)
        
        file_id = uuid.uuid4()
        encrypted_name = f"{file.filename}.arya"
        final_storage_path = storage_dir / f"{current_user.id}_{file_id}.arya"
        temp_storage_path = storage_dir / f"temp_{file_id}.enc"
        
        # 3. Streaming Encryption
        logger.info("[4/7] Streaming AES-256-GCM encryption (64 KB chunks)")
        with open(temp_storage_path, "wb") as temp_out:
            tag = AESManager.encrypt_stream(key, nonce, file.file, temp_out)
        logger.info(f"      auth_tag = {tag.hex()} ({len(tag)} bytes GCM tag)")
            
        # 4. Generate Metadata Header
        logger.info("[5/7] Building .arya JSON header (magic=ARYA + length + metadata)")
        metadata = EncryptedFileMetadata.build(salt, nonce, tag)
        header_bytes = EncryptedFileMetadata.serialize_header(metadata)
        logger.info(f"      algorithm = {metadata['algorithm']}")
        logger.info(f"      framework = {metadata['framework_version']}")
        logger.info(f"      header    = {len(header_bytes)} bytes")
        
        # 5. Assemble Final Encrypted File (Header + Ciphertext)
        logger.info("[6/7] Assembling final vault file: [ARYA header] + [ciphertext]")
        with open(final_storage_path, "wb") as final_out:
            final_out.write(header_bytes)
            with open(temp_storage_path, "rb") as temp_in:
                shutil.copyfileobj(temp_in, final_out)
                
        # 6. Cleanup temporary file
        temp_storage_path.unlink()
        
        # 7. Database Record Creation
        file_size = final_storage_path.stat().st_size
        logger.info("[7/7] Persisting vault record to PostgreSQL")
        
        db_file = DBFile(
            id=file_id,
            user_id=current_user.id,
            original_name=file.filename,
            encrypted_name=encrypted_name,
            file_size_bytes=file_size,
            storage_path=str(final_storage_path)
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)

        logger.info(f"[ENCRYPT] DONE → {encrypted_name} ({file_size} bytes) id={file_id}")
        logger.info("=" * 64)
        
        return db_file
        
    except HTTPException:
        raise
    except (ValueError, TypeError, OverflowError) as e:
        if 'temp_storage_path' in locals() and temp_storage_path.exists():
            temp_storage_path.unlink()
        logger.error(f"[ENCRYPT] Aryabhata rejected password: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        if 'temp_storage_path' in locals() and temp_storage_path.exists():
            temp_storage_path.unlink()
        logger.error(f"[ENCRYPT] FAILED: {e}")
        raise HTTPException(status_code=500, detail=f"Encryption failed: {str(e)}")


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
    """
    temp_id = uuid.uuid4()
    temp_decrypted_path = storage_dir / f"decrypted_{temp_id}.tmp"

    try:
        _log_crypto_banner(f"[DECRYPT] Starting for '{source_label}' (user={user_id})")

        logger.info("[1/5] Parsing ARYA header (magic + JSON metadata)")
        metadata, header_len = EncryptedFileMetadata.deserialize_from_stream(in_stream)
        algorithm = metadata.get("algorithm", AryabhataPreprocessor.ALGORITHM_ID)
        use_aryabhata = AryabhataPreprocessor.uses_aryabhata(algorithm)
        logger.info(f"      header_bytes={header_len}  algorithm={algorithm}")
        logger.info(f"      aryabhata_layer={'ON' if use_aryabhata else 'OFF (legacy file)'}")

        salt = base64.b64decode(metadata["salt"])
        nonce = base64.b64decode(metadata["nonce"])
        auth_tag = base64.b64decode(metadata["auth_tag"])
        logger.info(f"      salt={salt.hex()[:24]}...  nonce={nonce.hex()}  tag={auth_tag.hex()}")

        logger.info("[2/5] Password -> key material")
        if use_aryabhata and len(password) < MIN_PASSWORD_LENGTH:
            raise HTTPException(
                status_code=400,
                detail=f"Password must be at least {MIN_PASSWORD_LENGTH} characters for Aryabhata preprocessing.",
            )

        logger.info("[3/5] Derive AES-256 key")
        key = _derive_key_from_password(
            password,
            salt,
            use_aryabhata=use_aryabhata,
            log=True,
        )

        logger.info("[4/5] Streaming AES-256-GCM decryption + Auth Tag verify")
        with open(temp_decrypted_path, "wb") as temp_out:
            AESManager.decrypt_stream(key, nonce, auth_tag, in_stream, temp_out)

        logger.info("[5/5] Auth Tag OK — integrity verified, returning plaintext")
        logger.info("=" * 64)
        return temp_decrypted_path

    except HTTPException:
        if temp_decrypted_path.exists():
            temp_decrypted_path.unlink()
        raise
    except MetadataError as me:
        if temp_decrypted_path.exists():
            temp_decrypted_path.unlink()
        logger.error(f"[DECRYPT] Invalid format: {me}")
        raise HTTPException(status_code=400, detail=f"Invalid file format: {str(me)}")
    except AESGCMDecryptionError:
        if temp_decrypted_path.exists():
            temp_decrypted_path.unlink()
        logger.error("[DECRYPT] Auth failed — wrong password or tampered ciphertext")
        raise HTTPException(
            status_code=401,
            detail="Authentication failed: Incorrect password or tampered file.",
        )
    except (ValueError, TypeError, OverflowError) as e:
        if temp_decrypted_path.exists():
            temp_decrypted_path.unlink()
        logger.error(f"[DECRYPT] Aryabhata rejected password: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        if temp_decrypted_path.exists():
            temp_decrypted_path.unlink()
        logger.error(f"[DECRYPT] FAILED: {e}")
        raise HTTPException(status_code=500, detail=f"Decryption failed: {str(e)}")


@router.post("/decrypt")
def decrypt_file(
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

    storage_dir = Path(settings.UPLOAD_DIR)
    storage_dir.mkdir(parents=True, exist_ok=True)

    temp_decrypted_path = _decrypt_arya_stream_to_temp(
        in_stream=file.file,
        password=password,
        source_label=file.filename,
        user_id=current_user.id,
        storage_dir=storage_dir,
    )

    background_tasks.add_task(remove_file, temp_decrypted_path)

    original_filename = file.filename
    if original_filename.endswith(".arya"):
        original_filename = original_filename[:-5]

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

    storage_path = Path(file_record.storage_path)
    if not storage_path.exists():
        raise HTTPException(status_code=404, detail="Encrypted file missing from vault storage.")

    storage_dir = Path(settings.UPLOAD_DIR)
    storage_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"[VAULT-DECRYPT] Opening stored .arya id={file_id} name={file_record.encrypted_name}")

    with open(storage_path, "rb") as in_stream:
        temp_decrypted_path = _decrypt_arya_stream_to_temp(
            in_stream=in_stream,
            password=password,
            source_label=f"vault:{file_record.encrypted_name}",
            user_id=current_user.id,
            storage_dir=storage_dir,
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
    files = db.query(DBFile)\
              .filter(DBFile.user_id == current_user.id)\
              .order_by(DBFile.created_at.desc())\
              .offset(skip).limit(limit).all()
              
    return files


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

    storage_path = Path(file_record.storage_path)
    if not storage_path.exists():
        raise HTTPException(status_code=404, detail="Encrypted file missing from vault storage.")

    logger.info(f"[DOWNLOAD] .arya -> {file_record.encrypted_name} (id={file_id}, user={current_user.id})")

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
        
    # 2. Safely Erase Physical File
    try:
        storage_path = Path(file_record.storage_path)
        if storage_path.exists():
            # In a true high-security environment, we would overwrite the bytes 
            # (e.g. DoD 5220.22-M) before unlinking, but standard unlink is sufficient here 
            # since the file is robustly encrypted with AES-256-GCM.
            storage_path.unlink()
    except Exception as e:
        # We catch exceptions here so that a missing physical file doesn't 
        # trap a 'zombie' record in the database.
        print(f"Warning: Failed to delete physical file {storage_path}: {e}")
        
    # 3. Erase Database Record
    db.delete(file_record)
    db.commit()
    
    return None
