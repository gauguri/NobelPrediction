from datetime import datetime
from typing import Any, Dict, List

from pydantic import BaseModel


class AwardEvent(BaseModel):
    award_name: str
    year: int


class Candidate(BaseModel):
    id: int
    full_name: str
    field: str
    affiliation: str | None = None
    headshot_url: str | None = None
    clarivate_laureate: bool
    awards: List[AwardEvent] = []

    class Config:
        orm_mode = True


class Prediction(BaseModel):
    candidate: Candidate
    prediction_year: int
    horizon: str
    probability: float
    top_features: Dict[str, float]
    shap_values: Dict[str, float]
    created_at: datetime


class PredictionResponse(BaseModel):
    field: str
    horizon: str
    generated_at: datetime
    predictions: List[Prediction]


class BacktestMetric(BaseModel):
    field: str
    metric: str
    value: float
    details: Dict[str, Any]


class BacktestResponse(BaseModel):
    field: str
    metrics: List[BacktestMetric]


class ReportResponse(BaseModel):
    field: str
    horizon: str
    generated_at: datetime
    pdf_path: str | None = None
    csv_path: str | None = None

