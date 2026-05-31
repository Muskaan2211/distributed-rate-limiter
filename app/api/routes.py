from fastapi import APIRouter, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

router = APIRouter()


@router.get("/")
def root():
    return {"message": "Distributed Rate Limiter is running"}


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/limited")
def limited():
    return {"message": "You reached the protected route"}


@router.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)