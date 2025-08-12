from fastapi import APIRouter

from .monitoring import router as monitoring_router

router = APIRouter()

router.include_router(monitoring_router)
