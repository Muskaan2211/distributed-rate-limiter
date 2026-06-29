from __future__ import annotations

from fastapi import APIRouter, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from app.core.config import get_settings
from app.core.redis import get_redis

router = APIRouter()


@router.get("/")
def root():
    settings = get_settings()
    return {
        "service": settings.app_name,
        "status": "running",
        "dashboard": "/dashboard",
        "docs": "/docs",
        "protected_demo": "/api/v1/limited",
    }


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/ready")
def ready():
    client = get_redis()
    client.ping()
    return {"status": "ready", "redis": "ok"}


@router.get("/api/v1/limited")
def limited():
    return {"message": "Request allowed by the distributed gateway", "limited": True}


@router.get("/api/v1/config")
def config():
    s = get_settings()
    return {
        "algorithm": s.rate_limit_algorithm,
        "token_bucket": {"capacity": s.token_bucket_capacity, "refill_rate_per_second": s.token_bucket_refill_rate},
        "sliding_window": {"limit": s.sliding_window_limit, "window_seconds": s.sliding_window_seconds},
        "api_key_header": s.api_key_header,
    }


@router.post("/api/v1/demo/reset")
def reset_demo_state():
    client = get_redis()
    deleted = 0
    for pattern in ("rl:tb:*", "rl:sw:*"):
        for key in client.scan_iter(pattern):
            deleted += client.delete(key)
    return {"status": "reset", "deleted_keys": deleted}


@router.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
