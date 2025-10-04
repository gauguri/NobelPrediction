import json
from datetime import datetime
from pathlib import Path
from typing import List

import pandas as pd
from prefect import flow, task

from app.core.config import get_settings
from app.core.database import db_session
from app.models.nobel import Candidate, FeatureSnapshot
from app.services.data_quality import validate_feature_table

settings = get_settings()


@task
def load_seed_candidates(seed_path: Path) -> List[dict]:
    with seed_path.open("r", encoding="utf-8") as f:
        return json.load(f)


@task
def upsert_candidates(records: List[dict]) -> None:
    with db_session() as session:
        for record in records:
            candidate = session.query(Candidate).filter_by(openalex_id=record["openalex_id"]).one_or_none()
            if candidate is None:
                candidate = Candidate(
                    openalex_id=record["openalex_id"],
                    full_name=record["full_name"],
                    field=record["field"],
                    affiliation=record["affiliation"],
                    country=record.get("country"),
                    headshot_url=record.get("headshot_url"),
                )
                session.add(candidate)
                session.flush()
            else:
                candidate.full_name = record["full_name"]
                candidate.field = record["field"]
                candidate.affiliation = record["affiliation"]
                candidate.country = record.get("country")
                candidate.headshot_url = record.get("headshot_url")

            features = record["features"]
            snapshot = (
                session.query(FeatureSnapshot)
                .filter_by(candidate_id=candidate.id, as_of_year=features["as_of_year"])
                .one_or_none()
            )
            if snapshot is None:
                snapshot = FeatureSnapshot(candidate_id=candidate.id, **features)
                session.add(snapshot)
            else:
                snapshot.total_citations = features["total_citations"]
                snapshot.h_index = features["h_index"]
                snapshot.recent_trend = features["recent_trend"]
                snapshot.seminal_score = features["seminal_score"]
                snapshot.award_count = features["award_count"]


@task
def persist_feature_table(records: List[dict], output_path: Path) -> Path:
    rows = []
    for record in records:
        entry = {
            "openalex_id": record["openalex_id"],
            "field": record["field"],
            **record["features"],
        }
        rows.append(entry)
    df = pd.DataFrame(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return output_path


@task
def run_data_quality(parquet_path: Path) -> dict:
    return validate_feature_table(parquet_path)


@flow(name="seed_etl")
def run_seed_etl() -> str:
    seed_path = settings.data_dir / "seed" / "physics_candidates.json"
    seed_records = load_seed_candidates(seed_path)
    upsert_candidates(seed_records)
    table_path = persist_feature_table(seed_records, settings.data_dir / "staging" / "physics_features.csv")
    dq_result = run_data_quality(table_path)
    if not dq_result["success"]:
        raise ValueError("Data quality checks failed")
    return f"seed-etl-{datetime.utcnow().isoformat()}"
