"""Simple in-memory sliding-window rate limits for auth and decrypt."""

from __future__ import annotations

import time
from collections import defaultdict, deque
from threading import Lock

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def _client_key(self, request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        if request.client:
            return request.client.host or "unknown"
        return "unknown"

    def _limited(self, key: str, limit: int, window: float = 60.0) -> bool:
        now = time.monotonic()
        with self._lock:
            bucket = self._hits[key]
            while bucket and now - bucket[0] > window:
                bucket.popleft()
            if len(bucket) >= limit:
                return True
            bucket.append(now)
            return False

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        method = request.method.upper()
        client = self._client_key(request)

        if method == "POST" and path.endswith("/auth/login"):
            if self._limited(f"auth:{client}", settings.AUTH_RATE_LIMIT_PER_MINUTE):
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too many authentication attempts. Try again later."},
                )
        elif method == "POST" and (
            path.rstrip("/").endswith("/files/decrypt")
            or (path.rstrip("/").endswith("/decrypt") and "/files/" in path)
        ):
            if self._limited(f"decrypt:{client}", settings.DECRYPT_RATE_LIMIT_PER_MINUTE):
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too many decrypt attempts. Try again later."},
                )

        return await call_next(request)
