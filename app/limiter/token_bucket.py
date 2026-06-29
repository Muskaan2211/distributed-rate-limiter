from __future__ import annotations

import time
import redis
from app.core.config import get_settings
from app.limiter.base import RateLimitDecision


class TokenBucketLimiter:
    """Token bucket implemented as one Redis Lua script for atomic read-update-write."""

    LUA_SCRIPT = """
    local tokens_key = KEYS[1]
    local ts_key = KEYS[2]
    local capacity = tonumber(ARGV[1])
    local refill_rate = tonumber(ARGV[2])
    local now = tonumber(ARGV[3])
    local cost = tonumber(ARGV[4])
    local ttl = tonumber(ARGV[5])

    local tokens = tonumber(redis.call('GET', tokens_key))
    if tokens == nil then tokens = capacity end

    local last_refill = tonumber(redis.call('GET', ts_key))
    if last_refill == nil then last_refill = now end

    local delta = math.max(0, now - last_refill)
    tokens = math.min(capacity, tokens + (delta * refill_rate))

    local allowed = 0
    local retry_after = 0
    if tokens >= cost then
        tokens = tokens - cost
        allowed = 1
    else
        retry_after = math.ceil((cost - tokens) / refill_rate)
        if retry_after < 1 then retry_after = 1 end
    end

    redis.call('SETEX', tokens_key, ttl, tokens)
    redis.call('SETEX', ts_key, ttl, now)
    local reset_after = math.ceil((capacity - tokens) / refill_rate)
    return {allowed, tostring(tokens), retry_after, reset_after}
    """

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.script = self.redis.register_script(self.LUA_SCRIPT)
        self.settings = get_settings()

    def allow(self, identity: str, cost: int = 1) -> RateLimitDecision:
        now = time.time()
        ttl = max(60, int(self.settings.token_bucket_capacity / self.settings.token_bucket_refill_rate) * 3)
        result = self.script(
            keys=[f"rl:tb:{identity}:tokens", f"rl:tb:{identity}:ts"],
            args=[self.settings.token_bucket_capacity, self.settings.token_bucket_refill_rate, now, cost, ttl],
        )
        allowed = int(result[0]) == 1
        remaining = max(0, int(float(result[1])))
        return RateLimitDecision(
            allowed=allowed,
            limit=self.settings.token_bucket_capacity,
            remaining=remaining,
            retry_after=int(result[2]),
            reset_after=int(result[3]),
            algorithm="token_bucket",
        )
