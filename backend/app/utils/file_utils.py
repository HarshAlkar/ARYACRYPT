import os
import uuid
from typing import Tuple

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".txt",
    ".docx",
    ".zip",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif"
}

def validate_file_extension(filename: str) -> bool:
    """
    Validates if a file extension is supported by AryaCrypt.
    """
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS

def generate_secure_filename(original_filename: str) -> Tuple[str, str]:
    """
    Generates a secure UUID-based filename while preserving the original extension.
    Returns a tuple of (secure_name, extension).
    """
    ext = os.path.splitext(original_filename)[1].lower()
    secure_name = f"{uuid.uuid4().hex}{ext}"
    return secure_name, ext
