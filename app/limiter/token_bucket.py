import time

from app.config import TOKEN_BUCKET_CAPACITY, TOKEN_BUCKET_REFILL_RATE
from app.redis_client import redis_client


class TokenBucketLimiter:
    LUA_SCRIPT = """
    local tokens_key = KEYS[1]
    local ts_key = KEYS[2]

    local capacity = tonumber(ARGV[1])
    local refill_rate = tonumber(ARGV[2])
    local now = tonumber(ARGV[3])
    local cost = tonumber(ARGV[4])

    if refill_rate <= 0 then
        refill_rate = 1
    end

    local tokens = tonumber(redis.call("GET", tokens_key))
    if tokens == nil then
        tokens = capacity
    end

    local last_refill = tonumber(redis.call("GET", ts_key))
    if last_refill == nil then
        last_refill = now
    end

    local delta = math.max(0, now - last_refill)
    local refill = delta * refill_rate
    tokens = math.min(capacity, tokens + refill)

    local allowed = 0
    local retry_after = 0

    if tokens >= cost then
        tokens = tokens - cost
        allowed = 1
    else
        local deficit = cost - tokens
        retry_after = math.ceil(deficit / refill_rate)
        if retry_after < 1 then
            retry_after = 1
        end
    end

    redis.call("SET", tokens_key, tokens)
    redis.call("SET", ts_key, now)

    return {allowed, tokens, retry_after}
    """

    def __init__(self):
        self.redis = redis_client
        self.script = self.redis.register_script(self.LUA_SCRIPT)

    def allow(self, key: str, cost: int = 1):
        tokens_key = f"rate_limit:token_bucket:{key}:tokens"
        ts_key = f"rate_limit:token_bucket:{key}:ts"
        now = time.time()

        result = self.script(
            keys=[tokens_key, ts_key],
            args=[TOKEN_BUCKET_CAPACITY, TOKEN_BUCKET_REFILL_RATE, now, cost],
        )

        allowed = int(result[0]) == 1
        remaining_tokens = max(0, int(float(result[1])))
        retry_after = int(result[2])

        return allowed, remaining_tokens, retry_after