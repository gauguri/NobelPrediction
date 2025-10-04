from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = [
    "openalex_id",
    "field",
    "total_citations",
    "h_index",
    "recent_trend",
    "seminal_score",
    "award_count",
]


def validate_feature_table(path: Path) -> dict:
    df = pd.read_csv(path)
    results = []
    success = True
    for column in REQUIRED_COLUMNS:
        column_exists = column in df.columns
        results.append({"expectation": f"column_exists::{column}", "success": column_exists})
        success = success and column_exists
        if column_exists:
            not_null = df[column].notnull().all()
            results.append({"expectation": f"not_null::{column}", "success": not_null})
            success = success and not_null
            if column in {"total_citations", "h_index", "award_count"}:
                non_negative = (df[column] >= 0).all()
                results.append({"expectation": f"non_negative::{column}", "success": non_negative})
                success = success and non_negative
    return {"success": success, "results": results}
