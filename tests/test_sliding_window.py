from app.limiter import sliding_window as sliding_window_module
from app.limiter.sliding_window import SlidingWindowLimiter


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


def test_sliding_window_allow(monkeypatch):
    monkeypatch.setattr(sliding_window_module, "redis_client", FakeRedis([1, 3, 0]))
    limiter = SlidingWindowLimiter()

    allowed, current_count, retry_after = limiter.allow("client-1")

    assert allowed is True
    assert current_count == 3
    assert retry_after == 0


def test_sliding_window_block(monkeypatch):
    monkeypatch.setattr(sliding_window_module, "redis_client", FakeRedis([0, 5, 2]))
    limiter = SlidingWindowLimiter()

    allowed, current_count, retry_after = limiter.allow("client-1")

    assert allowed is False
    assert current_count == 5
    assert retry_after == 2