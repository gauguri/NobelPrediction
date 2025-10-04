from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Optional

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.entities import Candidate, Prediction

settings = get_settings()
SHARED_DIR = (settings.shared_dir or Path(__file__).resolve().parents[3] / "shared").resolve()
EXPORT_DIR = SHARED_DIR / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)


FIELDS = {
    "physics": "Physics",
    "chemistry": "Chemistry",
    "medicine": "Physiology or Medicine",
    "economics": "Economics",
}


def _fetch_predictions(field: str, horizon: str, db: Session):
    return (
        db.query(Prediction)
        .join(Candidate)
        .filter(Prediction.field == field, Prediction.horizon == horizon)
        .order_by(Prediction.probability.desc())
        .limit(20)
        .all()
    )


def build_csv_report(field: str, horizon: str, db: Session) -> Optional[Path]:
    predictions = _fetch_predictions(field, horizon, db)
    if not predictions:
        return None

    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    path = EXPORT_DIR / f"{field}_{horizon}_{timestamp}.csv"

    header = [
        "rank",
        "full_name",
        "affiliation",
        "probability",
        "top_features",
    ]

    with path.open("w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([f"Nobel shortlist for {FIELDS.get(field, field.title())}"])
        writer.writerow(["Generated", datetime.utcnow().isoformat()])
        writer.writerow([])
        writer.writerow(header)
        for idx, prediction in enumerate(predictions, start=1):
            writer.writerow(
                [
                    idx,
                    prediction.candidate.full_name,
                    prediction.candidate.affiliation,
                    round(prediction.probability, 4),
                    ", ".join(
                        f"{feat}: {weight:.3f}" for feat, weight in prediction.top_features.items()
                    ),
                ]
            )

    return path


def build_pdf_report(field: str, horizon: str, db: Session) -> Optional[Path]:
    predictions = _fetch_predictions(field, horizon, db)
    if not predictions:
        return None

    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    path = EXPORT_DIR / f"{field}_{horizon}_{timestamp}.pdf"

    c = canvas.Canvas(str(path), pagesize=letter)
    width, height = letter
    y = height - 72

    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, y, f"Nobel Prize Predictions – {FIELDS.get(field, field.title())}")
    y -= 24

    c.setFont("Helvetica", 10)
    c.drawString(72, y, f"Generated: {datetime.utcnow().isoformat()}")
    y -= 24

    c.setFont("Helvetica", 12)
    for idx, prediction in enumerate(predictions, start=1):
        if y < 100:
            c.showPage()
            y = height - 72
            c.setFont("Helvetica", 12)
        c.drawString(72, y, f"{idx}. {prediction.candidate.full_name} ({prediction.candidate.affiliation})")
        y -= 14
        c.setFont("Helvetica-Oblique", 10)
        c.drawString(72, y, f"Probability: {prediction.probability:.2%}")
        y -= 12
        feature_text = ", ".join(
            f"{feat}: {weight:.3f}" for feat, weight in prediction.top_features.items()
        )
        c.drawString(72, y, f"Drivers: {feature_text}")
        y -= 18
        c.setFont("Helvetica", 12)

    c.save()
    return path

