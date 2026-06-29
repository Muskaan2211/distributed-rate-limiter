from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.api.routes import router
from app.core.config import get_settings
from app.middleware.rate_limiter import RateLimitMiddleware

settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Redis-backed distributed rate limiter and API gateway with token bucket and sliding window algorithms.",
)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.add_middleware(RateLimitMiddleware)
app.include_router(router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/dashboard", include_in_schema=False)
def dashboard():
    return FileResponse("app/static/index.html")
