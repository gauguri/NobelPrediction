import json
from datetime import datetime
from pathlib import Path
from typing import List

import pandas as pd
from app.utils.prefect_compat import flow, task

from app.core.config import get_settings
from app.core.database import db_session
from app.models.nobel import Candidate, FeatureSnapshot
from app.services.data_quality import validate_feature_table

settings = get_settings()


@task
def discover_candidate_seed_files(seed_dir: Path) -> List[Path]:
    return sorted(seed_dir.glob("*_candidates.json"))


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
                    is_laureate=record.get("is_laureate", False),
                )
                session.add(candidate)
                session.flush()
            else:
                candidate.full_name = record["full_name"]
                candidate.field = record["field"]
                candidate.affiliation = record["affiliation"]
                candidate.country = record.get("country")
                candidate.headshot_url = record.get("headshot_url")
                candidate.is_laureate = record.get("is_laureate", False)

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
            "is_laureate": record.get("is_laureate", False),
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
    seed_dir = settings.data_dir / "seed"
    seed_files = discover_candidate_seed_files(seed_dir)
    if not seed_files:
        raise FileNotFoundError(f"No seed candidate files found in {seed_dir}")

    processed_fields: List[str] = []
    for seed_path in seed_files:
        seed_records = load_seed_candidates(seed_path)
        if not seed_records:
            continue

        field_name = seed_records[0]["field"]
        if any(record["field"] != field_name for record in seed_records):
            raise ValueError(f"Mixed fields detected in seed file {seed_path}")

        upsert_candidates(seed_records)
        field_slug = field_name.lower().replace(" ", "_")
        table_path = persist_feature_table(
            seed_records,
            settings.data_dir / "staging" / f"{field_slug}_features.csv",
        )
        dq_result = run_data_quality(table_path)
        if not dq_result["success"]:
            raise ValueError(f"Data quality checks failed for field {field_name}")
        processed_fields.append(field_name)

    fields_fragment = ",".join(processed_fields)
    return f"seed-etl-{datetime.utcnow().isoformat()}::{fields_fragment}"
