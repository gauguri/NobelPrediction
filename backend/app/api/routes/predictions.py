from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.entities import BacktestMetric, Candidate, Prediction as PredictionModel
from app.schemas.prediction import BacktestMetric as BacktestMetricSchema
from app.schemas.prediction import BacktestResponse, PredictionResponse

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.get("/{field}", response_model=PredictionResponse)
def get_predictions(field: str, horizon: str = "one_year", db: Session = Depends(get_db)) -> PredictionResponse:
    predictions: List[PredictionModel] = (
        db.query(PredictionModel)
        .join(Candidate)
        .filter(PredictionModel.field == field, PredictionModel.horizon == horizon)
        .order_by(PredictionModel.probability.desc())
        .limit(20)
        .all()
    )

    if not predictions:
        raise HTTPException(status_code=404, detail=f"No predictions found for field={field}")

    return PredictionResponse(
        field=field,
        horizon=horizon,
        generated_at=datetime.utcnow(),
        predictions=[
            {
                "candidate": prediction.candidate,
                "prediction_year": prediction.prediction_year,
                "horizon": prediction.horizon,
                "probability": prediction.probability,
                "top_features": prediction.top_features or {},
                "shap_values": prediction.shap_values or {},
                "created_at": prediction.created_at,
            }
            for prediction in predictions
        ],
    )


@router.get("/{field}/backtests", response_model=BacktestResponse)
def get_backtests(field: str, db: Session = Depends(get_db)) -> BacktestResponse:
    metrics: List[BacktestMetric] = db.query(BacktestMetric).filter(BacktestMetric.field == field).all()

    if not metrics:
        raise HTTPException(status_code=404, detail=f"No backtests found for field={field}")

    return BacktestResponse(
        field=field,
        metrics=[
            BacktestMetricSchema(
                field=metric.field,
                metric=metric.metric,
                value=metric.value,
                details=metric.details or {},
            )
            for metric in metrics
        ],
    )

