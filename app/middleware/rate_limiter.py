import os
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.limiter.sliding_window import SlidingWindowLimiter
from app.limiter.token_bucket import TokenBucketLimiter
from app.config import RATE_LIMIT_ALGORITHM


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.algorithm = RATE_LIMIT_ALGORITHM
        self.token_bucket = TokenBucketLimiter()
        self.sliding_window = SlidingWindowLimiter()

    async def dispatch(self, request: Request, call_next):
        if request.url.path in {"/", "/health", "/docs", "/openapi.json"}:
            return await call_next(request)

        client_ip = request.client.host if request.client else "anonymous"
        api_key = request.headers.get("X-API-Key", client_ip)

        if self.algorithm == "sliding_window":
            allowed, _ = self.sliding_window.allow(api_key)
        else:
            allowed, _ = self.token_bucket.allow(api_key)

        if not allowed:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests"},
            )

        return await call_next(request)