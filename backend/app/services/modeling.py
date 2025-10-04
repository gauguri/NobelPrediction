from __future__ import annotations

from pathlib import Path
from typing import Dict

import joblib
import numpy as np
import pandas as pd
from shap import KernelExplainer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.models.entities import BacktestMetric, Candidate, Prediction

settings = get_settings()
SHARED_DIR = (settings.shared_dir or Path(__file__).resolve().parents[3] / "shared").resolve()
ARTIFACT_DIR = SHARED_DIR / "artifacts"
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)


FEATURE_COLUMNS = [
    "total_citations",
    "field_normalized_citations",
    "h_index",
    "award_count",
    "topic_momentum",
    "clarivate_flag",
]


def _load_seed_features() -> pd.DataFrame:
    data_path = SHARED_DIR / "data" / "physics_features.csv"
    if not data_path.exists():
        raise FileNotFoundError("Seed feature dataset missing. Run ETL first.")
    df = pd.read_csv(data_path)
    return df


def _train_logistic(X: np.ndarray, y: np.ndarray) -> LogisticRegression:
    model = LogisticRegression(max_iter=1000, penalty="elasticnet", solver="saga", l1_ratio=0.5)
    model.fit(X, y)
    return model


def _train_xgb(X: np.ndarray, y: np.ndarray) -> XGBClassifier:
    model = XGBClassifier(
        n_estimators=50,
        max_depth=3,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        eval_metric="logloss",
        use_label_encoder=False,
    )
    model.fit(X, y)
    return model


def _train_lgbm(X: np.ndarray, y: np.ndarray) -> LGBMClassifier:
    model = LGBMClassifier(n_estimators=50, max_depth=-1, learning_rate=0.1)
    model.fit(X, y)
    return model


def train_models() -> Dict[str, str]:
    df = _load_seed_features()
    X = df[FEATURE_COLUMNS].values
    y = df["nobel_laureate"].values

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.3, random_state=42)

    logistic_model = _train_logistic(X_train, y_train)
    xgb_model = _train_xgb(X_train, y_train)
    lgbm_model = _train_lgbm(X_train, y_train)

    models = {
        "logistic": logistic_model,
        "xgboost": xgb_model,
        "lightgbm": lgbm_model,
    }

    artifact_paths: Dict[str, str] = {}
    joblib.dump(scaler, ARTIFACT_DIR / "physics_scaler.joblib")
    artifact_paths["scaler"] = str(ARTIFACT_DIR / "physics_scaler.joblib")

    for name, model in models.items():
        path = ARTIFACT_DIR / f"physics_{name}.joblib"
        joblib.dump(model, path)
        artifact_paths[name] = str(path)

    # Generate predictions on full dataset using ensemble average
    scaler_loaded: StandardScaler = joblib.load(ARTIFACT_DIR / "physics_scaler.joblib")
    X_full = scaler_loaded.transform(X)
    preds = {
        name: joblib.load(ARTIFACT_DIR / f"physics_{name}.joblib").predict_proba(X_full)[:, 1]
        for name in models
    }
    ensemble_prob = np.mean(np.stack(list(preds.values()), axis=0), axis=0)
    df["probability_one_year"] = ensemble_prob
    df["probability_three_year"] = np.clip(ensemble_prob * 1.5, 0, 1)

    # Compute SHAP values using KernelExplainer for transparency (toy)
    background = X_full[: min(5, len(X_full))]
    explainer = KernelExplainer(logistic_model.predict_proba, background)
    shap_values = explainer.shap_values(X_full, nsamples=50)[1]
    shap_df = pd.DataFrame(shap_values, columns=FEATURE_COLUMNS)

    df = df.join(shap_df.add_prefix("shap_"))

    predictions_path = ARTIFACT_DIR / "physics_predictions.csv"
    df.to_csv(predictions_path, index=False)
    artifact_paths["predictions"] = str(predictions_path)

    # Simple evaluation metrics stored for backtesting display
    y_proba = ensemble_prob
    eval_metrics = {
        "brier_score": float(brier_score_loss(y, y_proba)),
        "average_precision": float(average_precision_score(y, y_proba)),
    }
    pd.Series(eval_metrics).to_json(ARTIFACT_DIR / "physics_metrics.json")

    return artifact_paths


def _load_candidate_metadata() -> pd.DataFrame:
    meta_path = SHARED_DIR / "data" / "physics_candidates.csv"
    if not meta_path.exists():
        raise FileNotFoundError("Candidate metadata missing")
    return pd.read_csv(meta_path)


def update_predictions_from_artifacts() -> None:
    predictions_path = ARTIFACT_DIR / "physics_predictions.csv"
    if not predictions_path.exists():
        raise FileNotFoundError("Predictions artifact not found; run training first")

    df_pred = pd.read_csv(predictions_path)
    metadata = _load_candidate_metadata()
    merged = df_pred.merge(metadata, on="author_id", how="left")

    shap_cols = [col for col in merged.columns if col.startswith("shap_")]

    session = SessionLocal()
    try:
        field_name = str(merged.iloc[0]["field"]) if not merged.empty else "physics"
        for _, row in merged.iterrows():
            candidate = (
                session.query(Candidate)
                .filter(Candidate.full_name == row["full_name"], Candidate.field == row["field"])
                .one_or_none()
            )
            if candidate is None:
                candidate = Candidate(
                    full_name=row["full_name"],
                    field=row["field"],
                    affiliation=row["affiliation"],
                    headshot_url=row["headshot_url"],
                    openalex_id=row["openalex_id"],
                    clarivate_laureate=bool(row.get("clarivate_flag", False)),
                )
                session.add(candidate)
                session.flush()

            for horizon in ["one_year", "three_year"]:
                probability = row[f"probability_{horizon}"]
                shap_payload = {col.replace("shap_", ""): float(row[col]) for col in shap_cols}
                top_features = dict(sorted(shap_payload.items(), key=lambda item: abs(item[1]), reverse=True)[:5])

                prediction = (
                    session.query(Prediction)
                    .filter(
                        Prediction.candidate_id == candidate.id,
                        Prediction.prediction_year == int(row["prediction_year"]),
                        Prediction.horizon == horizon,
                    )
                    .one_or_none()
                )
                if prediction is None:
                    prediction = Prediction(
                        candidate_id=candidate.id,
                        prediction_year=int(row["prediction_year"]),
                        field=row["field"],
                        horizon=horizon,
                        probability=float(probability),
                        shap_values=shap_payload,
                        top_features=top_features,
                    )
                    session.add(prediction)
                else:
                    prediction.probability = float(probability)
                    prediction.shap_values = shap_payload
                    prediction.top_features = top_features
        # Upsert evaluation metrics for dashboard
        metrics_path = ARTIFACT_DIR / "physics_metrics.json"
        if metrics_path.exists():
            metrics = pd.read_json(metrics_path, typ="series")
            for metric_name, value in metrics.items():
                metric = (
                    session.query(BacktestMetric)
                    .filter(BacktestMetric.field == field_name, BacktestMetric.metric == metric_name)
                    .one_or_none()
                )
                payload = {
                    "field": field_name,
                    "metric": metric_name,
                    "value": float(value),
                    "details": {"timeframe": "2000-2020", "notes": "Toy data"},
                }
                if metric is None:
                    session.add(BacktestMetric(**payload))
                else:
                    metric.value = float(value)
                    metric.details = payload["details"]
        session.commit()
    finally:
        session.close()

