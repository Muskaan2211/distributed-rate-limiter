from __future__ import annotations

from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Distributed Rate Limiter & API Gateway"
    environment: str = "local"
    redis_url: str = "redis://localhost:6379/0"
    rate_limit_algorithm: str = Field(default="token_bucket", pattern="^(token_bucket|sliding_window)$")
    token_bucket_capacity: int = 100
    token_bucket_refill_rate: float = 50.0
    sliding_window_limit: int = 100
    sliding_window_seconds: int = 60
    api_key_header: str = "X-API-Key"
    ignored_paths: set[str] = {
        "/",
        "/health",
        "/ready",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/metrics",
        "/dashboard",
        "/favicon.ico",
    }
    cors_origins: list[str] = ["*"]
    redis_fail_open: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)


@lru_cache
def get_settings() -> Settings:
    return Settings()
