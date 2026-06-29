from __future__ import annotations

import time
import redis
from app.core.config import get_settings
from app.limiter.base import RateLimitDecision


class SlidingWindowLimiter:
    """Sliding window log using Redis sorted sets and Lua for atomic concurrency safety."""

    LUA_SCRIPT = """
    local key = KEYS[1]
    local now = tonumber(ARGV[1])
    local window = tonumber(ARGV[2])
    local limit = tonumber(ARGV[3])
    local member = ARGV[4]

    redis.call('ZREMRANGEBYSCORE', key, 0, now - window)
    local current = redis.call('ZCARD', key)
    local allowed = 0

    if current < limit then
        redis.call('ZADD', key, now, member)
        redis.call('EXPIRE', key, math.ceil(window))
        current = current + 1
        allowed = 1
    end

    local oldest = redis.call('ZRANGE', key, 0, 0, 'WITHSCORES')
    local retry_after = 0
    if allowed == 0 and oldest[2] ~= nil then
        retry_after = math.ceil((tonumber(oldest[2]) + window) - now)
        if retry_after < 1 then retry_after = 1 end
    end

    return {allowed, current, retry_after, math.ceil(window)}
    """

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.script = self.redis.register_script(self.LUA_SCRIPT)
        self.settings = get_settings()

    def allow(self, identity: str) -> RateLimitDecision:
        now = time.time()
        member = f"{now}:{time.perf_counter_ns()}"
        result = self.script(
            keys=[f"rl:sw:{identity}"],
            args=[now, self.settings.sliding_window_seconds, self.settings.sliding_window_limit, member],
        )
        allowed = int(result[0]) == 1
        used = int(result[1])
        return RateLimitDecision(
            allowed=allowed,
            limit=self.settings.sliding_window_limit,
            remaining=max(0, self.settings.sliding_window_limit - used),
            retry_after=int(result[2]),
            reset_after=int(result[3]),
            algorithm="sliding_window",
        )
