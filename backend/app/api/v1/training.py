from typing import Dict, TypedDict

from fastapi import APIRouter

from app.services.training_service import TrainingService

router = APIRouter()
service = TrainingService()


class ModelTrainingDetails(TypedDict):
    model_paths: Dict[str, str]
    prediction_count: int
    run_id: str


class TrainModelResponse(TypedDict):
    status: str
    details: ModelTrainingDetails


@router.post("/etl")
def run_etl() -> dict[str, str]:
    run_id = service.run_etl()
    return {"status": "completed", "run_id": run_id}


@router.post("/model")
def train_model() -> TrainModelResponse:
    model_info = service.train_models()
    return {"status": "trained", "details": model_info}
