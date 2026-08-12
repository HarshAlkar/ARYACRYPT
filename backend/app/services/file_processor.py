import base64
from pathlib import Path
from typing import Set, Dict

# FastAPI specific imports for handling HTTP file uploads
from fastapi import UploadFile

from app.services.encryption_service import EncryptionService
from app.services.decryption_service import DecryptionService
from app.crypto.aes import AESGCMDecryptionError


class FileProcessingError(Exception):
    """Raised when file validation or processing fails."""
    pass


class FileProcessorService:
    """
    Handles the complete lifecycle of file encryption and decryption.
    
    Responsibilities:
    - Validate allowed file extensions (PDF, PNG, JPG, JPEG, TXT, DOCX, XLSX, PPTX, ZIP).
    - Read and write file streams in memory-safe chunks.
    - Orchestrate the AryaCrypt encryption and decryption services.
    - Construct and parse the custom `.arya` binary file format header.
    """
    
    # Strictly enforced allowed extensions
    ALLOWED_EXTENSIONS: Set[str] = {
        ".pdf", ".png", ".jpg", ".jpeg", ".txt", ".docx", ".xlsx", ".pptx", ".zip"
    }
    
    # Custom File Format Header Magic Bytes (4 bytes) + Version (1 byte)
    MAGIC_BYTES = b"ARYA"
    VERSION = b"\x01"
    
    # Total Header Size: 4 (Magic) + 1 (Ver) + 16 (Salt) + 12 (Nonce) + 16 (Tag) = 49 bytes
    HEADER_SIZE_BYTES = 49

    def __init__(self, storage_dir: str = "local_storage/"):
        """
        Initializes the processor and ensures the storage directory exists.
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.enc_service = EncryptionService()
        self.dec_service = DecryptionService()

    def _validate_extension(self, filename: str) -> None:
        """Validates if the uploaded file matches the supported formats."""
        if not filename:
            raise FileProcessingError("Filename cannot be empty.")
            
        ext = Path(filename).suffix.lower()
        if ext not in self.ALLOWED_EXTENSIONS:
            raise FileProcessingError(
                f"Unsupported file format: '{ext}'. "
                f"Allowed formats are: {', '.join(self.ALLOWED_EXTENSIONS)}"
            )

    def process_and_encrypt(self, upload_file: UploadFile, password: str) -> Dict[str, str]:
        """
        Validates the upload, streams it through AryaCrypt, and packages it 
        into a secure, standalone `.arya` binary file.
        
        Args:
            upload_file (UploadFile): The FastAPI uploaded file object.
            password (str): The raw user password.
            
        Returns:
            Dict[str, str]: Metadata regarding the saved file.
        """
        self._validate_extension(upload_file.filename)
        
        original_stem = Path(upload_file.filename).stem
        output_filename = f"{original_stem}.arya"
        output_path = self.storage_dir / output_filename
        
        # We must stream the file to disk. Because AES-GCM calculates the Auth Tag 
        # at the *end* of the encryption stream, we write a 49-byte placeholder 
        # header first, stream the ciphertext, and then rewind to overwrite the header.
        
        with open(output_path, "wb") as out_f:
            # 1. Write Header Placeholder
            out_f.write(b'\x00' * self.HEADER_SIZE_BYTES)
            
            # 2. Stream Encryption directly from the UploadFile spool
            metadata = self.enc_service.encrypt_file(password, upload_file.file, out_f)
            
            # 3. Decode the Base64 metadata back to raw bytes for binary header storage
            salt_bytes = base64.b64decode(metadata['salt'])
            nonce_bytes = base64.b64decode(metadata['nonce'])
            tag_bytes = base64.b64decode(metadata['auth_tag'])
            
            # 4. Seek to beginning (byte 0) and write the permanent header
            out_f.seek(0)
            out_f.write(self.MAGIC_BYTES)
            out_f.write(self.VERSION)
            out_f.write(salt_bytes)
            out_f.write(nonce_bytes)
            out_f.write(tag_bytes)
            
        return {
            "original_filename": upload_file.filename,
            "encrypted_filename": output_filename,
            "filepath": str(output_path),
            "status": "encrypted"
        }

    def process_and_decrypt(self, filepath: str, password: str, original_extension: str) -> str:
        """
        Reads a `.arya` file, parses the cryptographic header, streams the 
        decryption, and restores the original file format safely.
        
        Args:
            filepath (str): Path to the `.arya` encrypted file.
            password (str): The user's password.
            original_extension (str): The extension to restore (e.g., '.pdf').
            
        Returns:
            str: The filepath to the successfully decrypted plaintext file.
            
        Raises:
            FileProcessingError: On corrupted formats or missing files.
            AESGCMDecryptionError: On wrong password or tampered payloads.
        """
        input_path = Path(filepath)
        if not input_path.exists():
            raise FileProcessingError(f"Encrypted file not found at: {filepath}")
            
        # Ensure the extension we are restoring to is valid
        self._validate_extension(f"dummy{original_extension}")
            
        output_filename = f"{input_path.stem}_decrypted{original_extension}"
        output_path = self.storage_dir / output_filename
        
        with open(input_path, "rb") as in_f:
            # 1. Parse and Validate Header
            magic = in_f.read(4)
            if magic != self.MAGIC_BYTES:
                raise FileProcessingError("Invalid file format. Magic bytes 'ARYA' not found. This is not an AryaCrypt file.")
                
            version = in_f.read(1)
            if version != self.VERSION:
                raise FileProcessingError(f"Unsupported AryaCrypt file version: {version.hex()}")
                
            salt_bytes = in_f.read(16)
            nonce_bytes = in_f.read(12)
            tag_bytes = in_f.read(16)
            
            # 2. Serialize Metadata for the Decryption Service
            metadata = {
                "salt": base64.b64encode(salt_bytes).decode('utf-8'),
                "nonce": base64.b64encode(nonce_bytes).decode('utf-8'),
                "auth_tag": base64.b64encode(tag_bytes).decode('utf-8')
            }
            
            # 3. Stream Decryption
            # The remaining bytes in `in_f` are pure ciphertext
            try:
                with open(output_path, "wb") as out_f:
                    self.dec_service.decrypt_file(password, metadata, in_f, out_f)
            except AESGCMDecryptionError:
                # If decryption fails (e.g. wrong password), delete the partially written dummy file
                if output_path.exists():
                    output_path.unlink()
                raise
                
        return str(output_path)
