import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware
from app.core.logging import logger
from app.core.rate_limit import RateLimitMiddleware


class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        logger.info(f"{request.method} {request.url.path} completed in {process_time:.4f}s")
        return response


def setup_middleware(app):
    from app.core.config import settings

    # CORS: explicit origins only (never *); credentials required for refresh cookie
    origins = [str(origin).rstrip("/") for origin in settings.BACKEND_CORS_ORIGINS]
    if not origins:
        raise RuntimeError(
            "BACKEND_CORS_ORIGINS must list explicit origins (do not use '*')."
        )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Accept", "X-Requested-With"],
        expose_headers=["X-AryaCrypt-Pipeline", "Content-Disposition", "X-Process-Time"],
    )

    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(TimingMiddleware)

