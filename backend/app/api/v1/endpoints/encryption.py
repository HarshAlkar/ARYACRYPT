import os
from pathlib import Path
from typing import Any
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

# Dependency Injection for DB & Auth
from app.api import deps
from app.models.user import User
from app.models.file import File as DBFile

# Business Logic Services
from app.services.file_processor import FileProcessorService, FileProcessingError

# Cryptographic Exception Handling
from app.crypto.aes import AESGCMEncryptionError, AESGCMDecryptionError
from app.crypto.metadata import MetadataError


router = APIRouter()

# Instantiate the service singleton to reuse across requests
file_processor = FileProcessorService(storage_dir="local_storage/")


@router.post("/encrypt", status_code=status.HTTP_201_CREATED)
def encrypt_file_endpoint(
    upload_file: UploadFile = File(...),
    password: str = Form(..., min_length=8, description="The strong password for AryaCrypt diffusion"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Enterprise Encryption Pipeline:
    1. Authenticates the user via JWT.
    2. Receives a raw file and a plaintext password.
    3. Streams the file through the AryaCrypt AES-256-GCM engine.
    4. Packages the ciphertext and metadata into a standalone `.arya` binary.
    5. Stores the audit trail and file path in the PostgreSQL database.
    """
    try:
        # Process and encrypt the file locally (Memory-Safe)
        result = file_processor.process_and_encrypt(upload_file, password)
        
        # Calculate file size for DB tracking
        storage_path = Path(result["filepath"])
        file_size = storage_path.stat().st_size if storage_path.exists() else 0
        
        # Persist file metadata to the database
        new_file_record = DBFile(
            user_id=current_user.id,
            original_name=result["original_filename"],
            encrypted_name=result["encrypted_filename"],
            file_size_bytes=file_size,
            storage_path=result["filepath"]
        )
        db.add(new_file_record)
        db.commit()
        db.refresh(new_file_record)
        
        return {
            "message": "File successfully encrypted and secured.",
            "file_id": new_file_record.id,
            "original_filename": new_file_record.original_name,
            "encrypted_filename": new_file_record.encrypted_name
        }
        
    except FileProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AESGCMEncryptionError:
        raise HTTPException(status_code=500, detail="A critical cryptographic error occurred during encryption.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.post("/decrypt")
def decrypt_file_endpoint(
    file_id: str = Form(..., description="The UUID of the file record from the user's history"),
    password: str = Form(..., description="The password to unlock the AryaCrypt derivation"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Enterprise Decryption Pipeline:
    1. Validates JWT and retrieves the file record to ensure ownership.
    2. Parses the ARYA binary header to extract cryptographic metadata.
    3. Regenerates the AES Key via the AryaCrypt Linguistic framework + PBKDF2.
    4. Streams decryption while verifying the GCM Authentication Tag.
    5. Returns the restored plaintext file as a direct HTTP download.
    """
    # 1. Enforce Authorization - Verify file belongs to the logged-in user
    file_record = db.query(DBFile).filter(DBFile.id == file_id, DBFile.user_id == current_user.id).first()
    if not file_record:
        raise HTTPException(status_code=404, detail="Encrypted file record not found or access denied.")
        
    storage_path = Path(file_record.storage_path)
    if not storage_path.exists():
        raise HTTPException(status_code=404, detail="Physical encrypted file not found on the server.")

    try:
        # The file processor needs the original extension to format the output correctly
        original_extension = Path(file_record.original_name).suffix
        
        # 2. Process and Decrypt (Strictly validates the Auth Tag)
        decrypted_filepath = file_processor.process_and_decrypt(
            filepath=str(storage_path),
            password=password,
            original_extension=original_extension
        )
        
        # 3. Return as a streamable FileResponse to avoid loading large files into RAM
        return FileResponse(
            path=decrypted_filepath,
            filename=file_record.original_name,
            media_type="application/octet-stream"
        )
        
    except FileProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except MetadataError as e:
        raise HTTPException(status_code=400, detail=f"Corrupted cryptographic metadata: {str(e)}")
    except AESGCMDecryptionError:
        # Crucial security practice: Provide a generic error to prevent Cryptographic Oracle attacks
        raise HTTPException(
            status_code=401, 
            detail="Authentication failed: The password provided is incorrect or the file was maliciously tampered with."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
