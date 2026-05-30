from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="Distributed Rate Limiter")
app.include_router(router)