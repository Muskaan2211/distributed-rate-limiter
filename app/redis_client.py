import redis

from app.config import REDIS_DB, REDIS_HOST, REDIS_PORT

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True,
    socket_connect_timeout=2,
    socket_timeout=2,
    retry_on_timeout=True,
)