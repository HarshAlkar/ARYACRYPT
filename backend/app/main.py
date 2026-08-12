from fastapi import FastAPI
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.middleware import setup_middleware
from app.api.v1.api import api_router

# Setup basic logging
setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="Enterprise Backend for AryaCrypt - Secure Key Generation and File Encryption"
)

# Setup middleware (CORS, Timing)
setup_middleware(app)

# Include all API v1 routers
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}. Visit /docs for API documentation."}

# Trigger reload
