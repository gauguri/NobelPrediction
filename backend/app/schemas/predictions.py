from datetime import datetime
from typing import List

from pydantic import BaseModel


class ShapAttributionSchema(BaseModel):
    feature_name: str
    feature_value: float
    shap_value: float


class PredictionSchema(BaseModel):
    candidate_id: int
    candidate_name: str
    affiliation: str
    field: str
    headshot_url: str | None
    probability: float
    horizon: str
    year: int
    shap_values: List[ShapAttributionSchema]


class CandidateDetailSchema(BaseModel):
    candidate_id: int
    candidate_name: str
    affiliation: str
    country: str | None
    headshot_url: str | None
    field: str
    total_citations: int
    h_index: float
    recent_trend: float
    seminal_score: float
    award_count: int


class BacktestMetricSchema(BaseModel):
    field: str
    hit_at_10: float
    auc_pr: float
    brier_score: float
    years_covered: tuple[int, int]


class ProvenanceRecord(BaseModel):
    feature_name: str
    source: str
    as_of_date: datetime
    latency_days: int


class ProvenanceResponse(BaseModel):
    candidate_id: int
    records: List[ProvenanceRecord]
