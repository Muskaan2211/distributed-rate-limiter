from app.limiter import token_bucket as token_bucket_module
from app.limiter.token_bucket import TokenBucketLimiter


class FakeScript:
    def __init__(self, result):
        self.result = result

    def __call__(self, keys=None, args=None):
        return self.result


class FakeRedis:
    def __init__(self, result):
        self.result = result

    def register_script(self, _script):
        return FakeScript(self.result)


def test_token_bucket_allow(monkeypatch):
    monkeypatch.setattr(token_bucket_module, "redis_client", FakeRedis([1, 4, 0]))
    limiter = TokenBucketLimiter()

    allowed, remaining, retry_after = limiter.allow("client-1")

    assert allowed is True
    assert remaining == 4
    assert retry_after == 0


def test_token_bucket_block(monkeypatch):
    monkeypatch.setattr(token_bucket_module, "redis_client", FakeRedis([0, 0, 3]))
    limiter = TokenBucketLimiter()

    allowed, remaining, retry_after = limiter.allow("client-1")

    assert allowed is False
    assert remaining == 0
    assert retry_after == 3