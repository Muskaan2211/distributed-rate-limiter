from __future__ import annotations

import hashlib
from fastapi import Request
from app.core.config import get_settings


def client_identity(request: Request) -> str:
    settings = get_settings()
    raw = request.headers.get(settings.api_key_header)
    if not raw:
        forwarded_for = request.headers.get("x-forwarded-for", "")
        raw = forwarded_for.split(",")[0].strip() or (request.client.host if request.client else "anonymous")
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]
