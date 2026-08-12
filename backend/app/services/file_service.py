import uuid
from typing import List
from sqlalchemy.orm import Session
from app.models.file import File

def create_file_record(db: Session, user_id: uuid.UUID, original_name: str, stored_name: str, mime_type: str, size_bytes: int) -> File:
    db_file = File(
        user_id=user_id,
        original_name=original_name,
        stored_name=stored_name,
        mime_type=mime_type,
        size_bytes=size_bytes
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

def get_file(db: Session, file_id: uuid.UUID, user_id: uuid.UUID) -> File | None:
    return db.query(File).filter(File.id == file_id, File.user_id == user_id).first()

def get_user_files(db: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[File]:
    return db.query(File).filter(File.user_id == user_id).offset(skip).limit(limit).all()

def delete_file_record(db: Session, db_file: File) -> None:
    db.delete(db_file)
    db.commit()
