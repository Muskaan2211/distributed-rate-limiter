import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.config import (
    API_KEY_HEADER,
    IGNORED_PATHS,
    RATE_LIMIT,
    RATE_LIMIT_ALGORITHM,
    TOKEN_BUCKET_CAPACITY,
)
from app.limiter.sliding_window import SlidingWindowLimiter
from app.limiter.token_bucket import TokenBucketLimiter
from app.metrics import REQUESTS_ALLOWED, REQUESTS_BLOCKED, REQUEST_LATENCY


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.algorithm = RATE_LIMIT_ALGORITHM
        self.token_bucket = TokenBucketLimiter()
        self.sliding_window = SlidingWindowLimiter()

    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()

        if request.url.path in IGNORED_PATHS:
            response = await call_next(request)
            REQUEST_LATENCY.observe(time.perf_counter() - start)
            return response

        client_ip = request.client.host if request.client else "anonymous"
        api_key = request.headers.get(API_KEY_HEADER, client_ip)

        if self.algorithm == "sliding_window":
            allowed, usage_value, retry_after = self.sliding_window.allow(api_key)
            limit_value = RATE_LIMIT
            remaining_value = max(0, limit_value - int(usage_value))
        else:
            allowed, tokens_left, retry_after = self.token_bucket.allow(api_key)
            limit_value = TOKEN_BUCKET_CAPACITY
            remaining_value = max(0, int(tokens_left))

        if not allowed:
            REQUESTS_BLOCKED.inc()
            REQUEST_LATENCY.observe(time.perf_counter() - start)
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests"},
                headers={
                    "X-RateLimit-Limit": str(limit_value),
                    "X-RateLimit-Remaining": str(remaining_value),
                    "Retry-After": str(max(1, retry_after)),
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit_value)
        response.headers["X-RateLimit-Remaining"] = str(remaining_value)
        REQUESTS_ALLOWED.inc()
        REQUEST_LATENCY.observe(time.perf_counter() - start)
        return response