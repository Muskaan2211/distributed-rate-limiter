from fastapi import FastAPI
from app.api.routes import router
from app.middleware.rate_limiter import RateLimitMiddleware

app = FastAPI(title="Distributed Rate Limiter")
app.add_middleware(RateLimitMiddleware)
app.include_router(router)