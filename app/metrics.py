from __future__ import annotations

from prometheus_client import Counter, Histogram, Gauge

REQUESTS_ALLOWED = Counter("rate_limiter_requests_allowed_total", "Allowed requests", ["algorithm", "path"])
REQUESTS_BLOCKED = Counter("rate_limiter_requests_blocked_total", "Blocked requests", ["algorithm", "path"])
REQUEST_LATENCY = Histogram("rate_limiter_request_latency_seconds", "Request latency", ["path"])
REDIS_HEALTH = Gauge("rate_limiter_redis_up", "Redis connectivity health")
