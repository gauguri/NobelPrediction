import json
from datetime import datetime
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd
from prefect import flow, task

from app.core.config import get_settings
from app.core.database import db_session
from app.models.nobel import Candidate, Prediction, ShapAttribution

settings = get_settings()


FEATURE_COLUMNS = [
    "total_citations",
    "h_index",
    "recent_trend",
    "seminal_score",
    "award_count",
]


@task
def load_feature_table(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


@task
def train_baseline_model(df: pd.DataFrame) -> tuple[dict, pd.DataFrame]:
    df = df.copy()
    rng = np.random.default_rng(seed=42)
    base_score = (
        0.000012 * df["total_citations"]
        + 0.002 * df["h_index"]
        + 0.15 * df["recent_trend"]
        + 0.08 * df["seminal_score"]
        + 0.03 * df["award_count"]
    )
    noise = rng.normal(scale=0.05, size=len(df))
    logits = base_score + noise
    probabilities = 1 / (1 + np.exp(-logits))
    df["probability_raw"] = probabilities
    model = {
        "coefficients": {
            "total_citations": 0.000012,
            "h_index": 0.002,
            "recent_trend": 0.15,
            "seminal_score": 0.08,
            "award_count": 0.03,
        },
        "intercept": -0.5,
    }
    return model, df


@task
def persist_model(model: dict, path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(model, f)
    return str(path)


@task
def generate_predictions(model: dict, df: pd.DataFrame, horizon: str) -> List[dict]:
    df = df.copy()
    logits = np.full(len(df), model["intercept"])
    for feature, coefficient in model["coefficients"].items():
        if feature in df:
            logits += coefficient * df[feature]
    probabilities = 1 / (1 + np.exp(-logits))
    df["probability"] = probabilities
    df["horizon"] = horizon
    df["year"] = datetime.utcnow().year
    return df.to_dict(orient="records")


@task
def persist_predictions(predictions: List[dict]) -> None:
    with db_session() as session:
        session.query(ShapAttribution).delete()
        session.query(Prediction).delete()
        session.flush()

        candidate_map = {c.openalex_id: c for c in session.query(Candidate).all()}
        for record in predictions:
            candidate = candidate_map.get(record["openalex_id"])
            if candidate is None:
                continue
            prediction = Prediction(
                candidate_id=candidate.id,
                year=record["year"],
                horizon=record["horizon"],
                probability=float(record["probability"]),
            )
            session.add(prediction)
            session.flush()
            shap_values = compute_simple_shap(record)
            for shap_entry in shap_values:
                session.add(
                    ShapAttribution(
                        prediction_id=prediction.id,
                        feature_name=shap_entry["feature_name"],
                        feature_value=float(shap_entry["feature_value"]),
                        shap_value=float(shap_entry["shap_value"]),
                    )
                )


@task
def compute_simple_shap(prediction_record: dict) -> List[dict]:
    feature_contributions = []
    baseline = 0.02
    for feature in FEATURE_COLUMNS:
        weight = {
            "total_citations": 1e-5,
            "h_index": 0.002,
            "recent_trend": 0.2,
            "seminal_score": 0.15,
            "award_count": 0.05,
        }[feature]
        value = prediction_record[feature]
        contribution = weight * value
        feature_contributions.append(
            {
                "feature_name": feature,
                "feature_value": value,
                "shap_value": contribution,
            }
        )
    return feature_contributions


@flow(name="baseline_model_training")
def run_model_training() -> dict:
    staging_path = settings.data_dir / "staging" / "physics_features.csv"
    df = load_feature_table(staging_path)
    model, augmented_df = train_baseline_model(df)
    model_path = settings.model_dir / "physics" / "baseline_model.joblib"
    persist_model(model, model_path)
    predictions = generate_predictions(model, augmented_df, "one_year")
    persist_predictions(predictions)
    return {
        "model_path": str(model_path),
        "prediction_count": len(predictions),
        "run_id": f"model-{datetime.utcnow().isoformat()}",
    }
