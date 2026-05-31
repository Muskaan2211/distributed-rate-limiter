from fastapi.testclient import TestClient

import app.main as main
from app.limiter.token_bucket import TokenBucketLimiter

client = TestClient(main.app)


def test_health_route():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_limited_route_headers(monkeypatch):
    monkeypatch.setattr(TokenBucketLimiter, "allow", lambda self, key, cost=1: (True, 4, 0))

    response = client.get("/limited")

    assert response.status_code == 200
    assert response.headers["x-ratelimit-limit"] == "5"
    assert response.headers["x-ratelimit-remaining"] == "4"


def test_limited_route_returns_429(monkeypatch):
    monkeypatch.setattr(TokenBucketLimiter, "allow", lambda self, key, cost=1: (False, 0, 2))

    response = client.get("/limited")

    assert response.status_code == 429
    assert response.json() == {"detail": "Too many requests"}
    assert response.headers["retry-after"] == "2"