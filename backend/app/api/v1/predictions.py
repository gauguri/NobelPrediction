from typing import List

from fastapi import APIRouter, HTTPException, Query

from app.schemas.predictions import (
    BacktestMetricSchema,
    CandidateDetailSchema,
    PredictionSchema,
    ProvenanceResponse,
)
from app.services.prediction_service import PredictionService

router = APIRouter()
service = PredictionService()


@router.get("/shortlist", response_model=List[PredictionSchema])
def shortlist(field: str = Query(...), horizon: str = Query("one_year")):
    return service.get_shortlist(field=field, horizon=horizon)


@router.get("/candidates/{candidate_id}", response_model=CandidateDetailSchema)
def candidate_detail(candidate_id: int):
    detail = service.get_candidate_detail(candidate_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return detail


@router.get("/backtests", response_model=List[BacktestMetricSchema])
def backtests(field: str | None = None):
    return service.get_backtests(field=field)


@router.get("/provenance/{candidate_id}", response_model=ProvenanceResponse)
def provenance(candidate_id: int):
    return service.get_provenance(candidate_id)
