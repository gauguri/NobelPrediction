from fastapi import APIRouter

from app.services.training_service import TrainingService

router = APIRouter()
service = TrainingService()


@router.post("/etl")
def run_etl() -> dict[str, str]:
    run_id = service.run_etl()
    return {"status": "completed", "run_id": run_id}


@router.post("/model")
def train_model() -> dict[str, str]:
    model_info = service.train_models()
    return {"status": "trained", "details": model_info}
