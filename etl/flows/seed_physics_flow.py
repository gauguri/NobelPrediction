from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List

import duckdb
import pandas as pd
from prefect import flow, task
import great_expectations as ge

BASE_DIR = Path(__file__).resolve().parents[2]
SHARED_DIR = BASE_DIR / "shared"
DATA_DIR = SHARED_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

RAW_DIR = SHARED_DIR / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)


@task
def load_seed_sources() -> pd.DataFrame:
    """Load or synthesize a toy dataset representing Physics candidates."""
    data = [
        {
            "author_id": "A1",
            "full_name": "Lene Hau",
            "affiliation": "Harvard University",
            "openalex_id": "A123",
            "headshot_url": "https://example.com/hau.jpg",
            "field": "physics",
            "total_citations": 12000,
            "field_normalized_citations": 98.5,
            "h_index": 65,
            "award_count": 4,
            "topic_momentum": 0.82,
            "clarivate_flag": 1,
            "nobel_laureate": 0,
            "prediction_year": 2024,
        },
        {
            "author_id": "A2",
            "full_name": "John Pendry",
            "affiliation": "Imperial College London",
            "openalex_id": "A456",
            "headshot_url": "https://example.com/pendry.jpg",
            "field": "physics",
            "total_citations": 18000,
            "field_normalized_citations": 97.1,
            "h_index": 80,
            "award_count": 5,
            "topic_momentum": 0.74,
            "clarivate_flag": 1,
            "nobel_laureate": 0,
            "prediction_year": 2024,
        },
        {
            "author_id": "A3",
            "full_name": "Alain Aspect",
            "affiliation": "Institut d'Optique",
            "openalex_id": "A789",
            "headshot_url": "https://example.com/aspect.jpg",
            "field": "physics",
            "total_citations": 22000,
            "field_normalized_citations": 99.2,
            "h_index": 90,
            "award_count": 6,
            "topic_momentum": 0.88,
            "clarivate_flag": 1,
            "nobel_laureate": 1,
            "prediction_year": 2022,
        },
        {
            "author_id": "A4",
            "full_name": "Donna Strickland",
            "affiliation": "University of Waterloo",
            "openalex_id": "A321",
            "headshot_url": "https://example.com/strickland.jpg",
            "field": "physics",
            "total_citations": 9000,
            "field_normalized_citations": 90.3,
            "h_index": 55,
            "award_count": 3,
            "topic_momentum": 0.65,
            "clarivate_flag": 0,
            "nobel_laureate": 1,
            "prediction_year": 2018,
        },
        {
            "author_id": "A5",
            "full_name": "Jun Ye",
            "affiliation": "JILA / University of Colorado",
            "openalex_id": "A654",
            "headshot_url": "https://example.com/junye.jpg",
            "field": "physics",
            "total_citations": 15000,
            "field_normalized_citations": 96.2,
            "h_index": 70,
            "award_count": 4,
            "topic_momentum": 0.79,
            "clarivate_flag": 0,
            "nobel_laureate": 0,
            "prediction_year": 2024,
        },
    ]
    return pd.DataFrame(data)


@task
def persist_to_duckdb(df: pd.DataFrame) -> Path:
    db_path = DATA_DIR / "physics.duckdb"
    conn = duckdb.connect(str(db_path))
    conn.register("df", df)
    conn.execute("CREATE TABLE IF NOT EXISTS physics_candidates AS SELECT * FROM df")
    conn.execute("DELETE FROM physics_candidates")
    conn.execute("INSERT INTO physics_candidates SELECT * FROM df")
    conn.close()
    return db_path


@task
def export_csv(df: pd.DataFrame) -> List[Path]:
    features_path = DATA_DIR / "physics_features.csv"
    candidates_path = DATA_DIR / "physics_candidates.csv"
    df.to_csv(features_path, index=False)
    df[[
        "author_id",
        "full_name",
        "affiliation",
        "openalex_id",
        "headshot_url",
        "field",
        "clarivate_flag",
    ]].to_csv(candidates_path, index=False)
    return [features_path, candidates_path]


@task
def write_provenance(records: pd.DataFrame) -> Path:
    provenance_path = DATA_DIR / "physics_provenance.csv"
    records.to_csv(provenance_path, index=False)
    return provenance_path


@task
def run_quality_checks(features_path: Path) -> dict[str, str]:
    df = pd.read_csv(features_path)
    dataset = ge.from_pandas(df)
    dataset.expect_table_row_count_to_be_between(min_value=1, max_value=1000)
    dataset.expect_column_values_to_not_be_null("author_id")
    dataset.expect_column_min_to_be_between("total_citations", min_value=0)
    result = dataset.validate()
    if not result.success:
        raise ValueError("Data quality checks failed")
    return {"status": "passed"}


@flow(name="seed_physics_flow")
def seed_physics_flow() -> dict[str, str]:
    df = load_seed_sources()
    persist_to_duckdb(df)
    features_path, _ = export_csv(df)
    provenance = pd.DataFrame(
        [
            {
                "feature_name": "total_citations",
                "source": "synthetic",
                "as_of_date": datetime.utcnow().date(),
                "latency_days": 0,
            },
            {
                "feature_name": "award_count",
                "source": "synthetic",
                "as_of_date": datetime.utcnow().date(),
                "latency_days": 0,
            },
        ]
    )
    write_provenance(provenance)
    run_quality_checks(features_path)
    return {"status": "completed", "rows": str(len(df))}


if __name__ == "__main__":
    seed_physics_flow()

