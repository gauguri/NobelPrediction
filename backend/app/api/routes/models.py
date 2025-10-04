from fastapi import APIRouter

from app.services.modeling import train_models, update_predictions_from_artifacts

router = APIRouter(prefix="/models", tags=["models"])


@router.post("/train")
def trigger_training() -> dict[str, str]:
    artifact_paths = train_models()
    update_predictions_from_artifacts()
    return {"status": "completed", "artifacts": artifact_paths}

