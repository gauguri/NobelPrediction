from fastapi import APIRouter

from . import predictions, system, reports, training

router = APIRouter()
router.include_router(system.router, tags=["system"])
router.include_router(training.router, prefix="/training", tags=["training"])
router.include_router(predictions.router, prefix="/predictions", tags=["predictions"])
router.include_router(reports.router, prefix="/reports", tags=["reports"])
