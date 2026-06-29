from __future__ import annotations

import redis
from app.core.config import get_settings


def get_redis() -> redis.Redis:
    settings = get_settings()
    return redis.Redis.from_url(
        settings.redis_url,
        decode_responses=True,
        socket_connect_timeout=1,
        socket_timeout=1,
        health_check_interval=30,
        retry_on_timeout=True,
    )
