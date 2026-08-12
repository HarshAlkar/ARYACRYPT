from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.api import deps
from app.core.config import settings

router = APIRouter()

@router.get("/")
def check_health(db: Session = Depends(deps.get_db)):
    """
    Health check API. Verifies if the backend is running and the database is accessible.
    """
    db_status = "ok"
    try:
        # Check DB connection
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "unreachable"

    return {
        "status": "ok",
        "version": settings.VERSION,
        "database": db_status
    }
