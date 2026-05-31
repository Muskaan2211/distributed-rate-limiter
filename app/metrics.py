from prometheus_client import Counter, Histogram

REQUESTS_ALLOWED = Counter(
    "rate_limiter_requests_allowed_total",
    "Total allowed requests",
)

REQUESTS_BLOCKED = Counter(
    "rate_limiter_requests_blocked_total",
    "Total blocked requests",
)

REQUEST_LATENCY = Histogram(
    "rate_limiter_request_latency_seconds",
    "Request latency in seconds",
)