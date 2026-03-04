from fastapi import APIRouter, HTTPException
import logging
from models import HealthResponse

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/",response_model=HealthResponse)
@router.head("/",response_model=HealthResponse)
async def health_check():
    return {"status": "ok"}
