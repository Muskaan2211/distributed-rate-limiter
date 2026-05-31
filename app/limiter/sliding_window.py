import time
import uuid

from app.config import RATE_LIMIT, WINDOW_SECONDS
from app.redis_client import redis_client


class SlidingWindowLimiter:
    LUA_SCRIPT = """
    local key = KEYS[1]
    local now = tonumber(ARGV[1])
    local window = tonumber(ARGV[2])
    local limit = tonumber(ARGV[3])
    local request_id = ARGV[4]

    redis.call("ZREMRANGEBYSCORE", key, 0, now - window)

    local current = redis.call("ZCARD", key)
    if current >= limit then
        local oldest = redis.call("ZRANGE", key, 0, 0, "WITHSCORES")
        local retry_after = 1
        if oldest[2] ~= nil then
            retry_after = math.ceil((tonumber(oldest[2]) + window) - now)
            if retry_after < 1 then
                retry_after = 1
            end
        end
        return {0, current, retry_after}
    end

    redis.call("ZADD", key, now, request_id)
    redis.call("EXPIRE", key, math.ceil(window))
    return {1, current + 1, 0}
    """

    def __init__(self):
        self.redis = redis_client
        self.script = self.redis.register_script(self.LUA_SCRIPT)

    def allow(self, key: str, limit: int = RATE_LIMIT):
        zset_key = f"rate_limit:sliding_window:{key}"
        now = time.time()
        request_id = str(uuid.uuid4())

        result = self.script(
            keys=[zset_key],
            args=[now, WINDOW_SECONDS, limit, request_id],
        )

        allowed = int(result[0]) == 1
        current_count = int(result[1])
        retry_after = int(result[2])

        return allowed, current_count, retry_after