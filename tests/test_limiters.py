import fakeredis
from app.limiter.sliding_window import SlidingWindowLimiter
from app.limiter.token_bucket import TokenBucketLimiter


def test_token_bucket_blocks_after_capacity(monkeypatch):
    monkeypatch.setenv('TOKEN_BUCKET_CAPACITY', '2')
    monkeypatch.setenv('TOKEN_BUCKET_REFILL_RATE', '0.01')
    from app.core.config import get_settings
    get_settings.cache_clear()
    limiter = TokenBucketLimiter(fakeredis.FakeRedis(decode_responses=True))
    assert limiter.allow('user-a').allowed is True
    assert limiter.allow('user-a').allowed is True
    assert limiter.allow('user-a').allowed is False


def test_sliding_window_blocks_after_limit(monkeypatch):
    monkeypatch.setenv('SLIDING_WINDOW_LIMIT', '2')
    monkeypatch.setenv('SLIDING_WINDOW_SECONDS', '60')
    from app.core.config import get_settings
    get_settings.cache_clear()
    limiter = SlidingWindowLimiter(fakeredis.FakeRedis(decode_responses=True))
    assert limiter.allow('user-b').allowed is True
    assert limiter.allow('user-b').allowed is True
    assert limiter.allow('user-b').allowed is False
