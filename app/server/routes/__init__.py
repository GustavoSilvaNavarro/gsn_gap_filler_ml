from fastapi import APIRouter

from .gap_filler import router as filler_router
from .monitoring import router as monitoring_router

router = APIRouter()

router.include_router(monitoring_router)
router.include_router(filler_router)
