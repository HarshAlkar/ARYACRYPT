from fastapi import APIRouter
from app.api.v1.endpoints import health, auth, files

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
# api_router.include_router(encryption.router, prefix="/encryption", tags=["encryption"])
