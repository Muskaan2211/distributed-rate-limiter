from __future__ import annotations

import time
import redis
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.core.config import get_settings
from app.core.identity import client_identity
from app.core.redis import get_redis
from app.limiter.sliding_window import SlidingWindowLimiter
from app.limiter.token_bucket import TokenBucketLimiter
from app.metrics import REQUESTS_ALLOWED, REQUESTS_BLOCKED, REQUEST_LATENCY, REDIS_HEALTH


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.settings = get_settings()
        self.redis = get_redis()
        self.token_bucket = TokenBucketLimiter(self.redis)
        self.sliding_window = SlidingWindowLimiter(self.redis)

    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        path = request.url.path
        if path.startswith("/static") or path in self.settings.ignored_paths:
            response = await call_next(request)
            REQUEST_LATENCY.labels(path=path).observe(time.perf_counter() - start)
            return response

        try:
            identity = client_identity(request)
            if self.settings.rate_limit_algorithm == "sliding_window":
                decision = self.sliding_window.allow(identity)
            else:
                decision = self.token_bucket.allow(identity)
            REDIS_HEALTH.set(1)
        except redis.RedisError as exc:
            REDIS_HEALTH.set(0)
            if self.settings.redis_fail_open:
                response = await call_next(request)
                response.headers["X-RateLimit-Policy"] = "fail-open"
                return response
            return JSONResponse(status_code=503, content={"detail": "Rate limiter backend unavailable", "error": str(exc)})

        headers = {
            "X-RateLimit-Algorithm": decision.algorithm,
            "X-RateLimit-Limit": str(decision.limit),
            "X-RateLimit-Remaining": str(decision.remaining),
            "X-RateLimit-Reset": str(decision.reset_after),
        }

        if not decision.allowed:
            REQUESTS_BLOCKED.labels(algorithm=decision.algorithm, path=path).inc()
            REQUEST_LATENCY.labels(path=path).observe(time.perf_counter() - start)
            headers["Retry-After"] = str(max(1, decision.retry_after))
            return JSONResponse(status_code=429, content={"detail": "Too many requests", "retry_after": decision.retry_after}, headers=headers)

        response = await call_next(request)
        for key, value in headers.items():
            response.headers[key] = value
        REQUESTS_ALLOWED.labels(algorithm=decision.algorithm, path=path).inc()
        REQUEST_LATENCY.labels(path=path).observe(time.perf_counter() - start)
        return response
