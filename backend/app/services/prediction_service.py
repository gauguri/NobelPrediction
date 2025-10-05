import json
from datetime import datetime
from typing import List

import pandas as pd

from fastapi import HTTPException, status

from app.core.config import get_settings
from app.core.database import db_session
from app.models.nobel import Candidate, FeatureSnapshot, Prediction
from app.schemas.predictions import (
    BacktestMetricSchema,
    CandidateDetailSchema,
    PredictionSchema,
    ProvenanceRecord,
    ProvenanceResponse,
    ShapAttributionSchema,
)

settings = get_settings()


class PredictionService:
    def get_shortlist(self, field: str, horizon: str) -> List[PredictionSchema]:
        with db_session() as session:
            query = (
                session.query(Prediction, Candidate)
                .join(Candidate, Candidate.id == Prediction.candidate_id)
                .filter(
                    Candidate.field == field,
                    Candidate.is_laureate.is_(False),
                    Prediction.horizon == horizon,
                )
                .order_by(Prediction.probability.desc())
                .limit(20)
            )
            results = []
            for prediction, candidate in query:
                shap_values = [
                    ShapAttributionSchema(
                        feature_name=shap.feature_name,
                        feature_value=shap.feature_value,
                        shap_value=shap.shap_value,
                    )
                    for shap in prediction.shap_values
                ]
                results.append(
                    PredictionSchema(
                        candidate_id=candidate.id,
                        candidate_name=candidate.full_name,
                        affiliation=candidate.affiliation,
                        field=candidate.field,
                        headshot_url=candidate.headshot_url,
                        probability=prediction.probability,
                        horizon=prediction.horizon,
                        year=prediction.year,
                        shap_values=shap_values,
                    )
                )
            return results

    def get_candidate_detail(self, candidate_id: int) -> CandidateDetailSchema | None:
        with db_session() as session:
            candidate = session.query(Candidate).filter_by(id=candidate_id).one_or_none()
            if candidate is None:
                return None
            snapshot = (
                session.query(FeatureSnapshot)
                .filter_by(candidate_id=candidate.id)
                .order_by(FeatureSnapshot.as_of_year.desc())
                .first()
            )
            if snapshot is None:
                return None
            return CandidateDetailSchema(
                candidate_id=candidate.id,
                candidate_name=candidate.full_name,
                affiliation=candidate.affiliation,
                country=candidate.country,
                headshot_url=candidate.headshot_url,
                field=candidate.field,
                total_citations=snapshot.total_citations,
                h_index=snapshot.h_index,
                recent_trend=snapshot.recent_trend,
                seminal_score=snapshot.seminal_score,
                award_count=snapshot.award_count,
            )

    def get_backtests(self, field: str | None) -> List[BacktestMetricSchema]:
        backtests_path = settings.data_dir / "seed" / "backtests.json"
        if not backtests_path.exists():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Backtest metrics are not available yet.",
            )
        df = pd.read_json(backtests_path)
        if field:
            df = df[df["field"] == field]
        results = []
        for row in df.to_dict(orient="records"):
            results.append(
                BacktestMetricSchema(
                    field=row["field"],
                    hit_at_10=row["hit_at_10"],
                    auc_pr=row["auc_pr"],
                    brier_score=row["brier_score"],
                    years_covered=tuple(row["years_covered"]),
                )
            )
        return results

    def get_provenance(self, candidate_id: int) -> ProvenanceResponse:
        with db_session() as session:
            candidate = session.query(Candidate).filter_by(id=candidate_id).one()
        provenance_path = settings.data_dir / "seed" / "provenance.json"
        with provenance_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        records = []
        for record in data.get(candidate.openalex_id, []):
            records.append(
                ProvenanceRecord(
                    feature_name=record["feature_name"],
                    source=record["source"],
                    as_of_date=datetime.fromisoformat(record["as_of_date"]),
                    latency_days=record["latency_days"],
                )
            )
        return ProvenanceResponse(candidate_id=candidate.id, records=records)
