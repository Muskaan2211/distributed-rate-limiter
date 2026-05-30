from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def root():
    return {"message": "Distributed Rate Limiter is running"}

@router.get("/health")
def health():
    return {"status": "ok"}