from pathlib import Path

import pandas as pd

from app.core.config import get_settings
from app.core.database import db_session
from app.models.nobel import Candidate, Prediction

settings = get_settings()


def _shortlist_dataframe(field: str, horizon: str) -> pd.DataFrame:
    with db_session() as session:
        query = (
            session.query(Prediction, Candidate)
            .join(Candidate, Candidate.id == Prediction.candidate_id)
            .filter(Candidate.field == field, Prediction.horizon == horizon)
            .order_by(Prediction.probability.desc())
        )
        rows = []
        for prediction, candidate in query:
            rows.append(
                {
                    "Rank": len(rows) + 1,
                    "Candidate": candidate.full_name,
                    "Affiliation": candidate.affiliation,
                    "Probability": round(prediction.probability, 3),
                }
            )
        return pd.DataFrame(rows)


def generate_csv_report(field: str, horizon: str) -> Path:
    df = _shortlist_dataframe(field, horizon)
    target = settings.data_dir / "reports" / f"shortlist_{field}_{horizon}.csv"
    target.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(target, index=False)
    return target


def generate_pdf_report(field: str, horizon: str) -> Path:
    df = _shortlist_dataframe(field, horizon)
    target = settings.data_dir / "reports" / f"shortlist_{field}_{horizon}.pdf"
    target.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"Nobel Prediction Shortlist - {field} ({horizon})", ""]
    if df.empty:
        lines.append("No predictions available.")
    else:
        for _, row in df.iterrows():
            lines.append(
                f"#{int(row['Rank'])} {row['Candidate']} — {row['Affiliation']} — P(win)={row['Probability']}"
            )
    _write_simple_pdf(target, lines)
    return target


def _write_simple_pdf(path: Path, lines: list[str]) -> None:
    def escape(text: str) -> str:
        return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    stream_lines = ["BT", "/F1 12 Tf"]
    y = 760
    for line in lines:
        stream_lines.append(f"1 0 0 1 50 {y} Tm ({escape(line)}) Tj")
        y -= 16
    stream_lines.append("ET")
    stream_bytes = "\n".join(stream_lines).encode("latin-1", errors="ignore")

    objects = []
    objects.append(b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n")
    objects.append(b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n")
    objects.append(
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj\n"
    )
    objects.append(b"4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n")
    length_header = f"5 0 obj << /Length {len(stream_bytes)} >> stream\n".encode("latin-1")
    objects.append(length_header + stream_bytes + b"\nendstream\nendobj\n")

    with path.open("wb") as f:
        f.write(b"%PDF-1.4\n")
        offsets = [0]
        for obj in objects:
            offsets.append(f.tell())
            f.write(obj)
        xref_start = f.tell()
        f.write(f"xref\n0 {len(objects)+1}\n".encode("latin-1"))
        f.write(b"0000000000 65535 f \n")
        for offset in offsets[1:]:
            f.write(f"{offset:010} 00000 n \n".encode("latin-1"))
        f.write(b"trailer << /Size 6 /Root 1 0 R >>\n")
        f.write(b"startxref\n")
        f.write(f"{xref_start}\n".encode("latin-1"))
        f.write(b"%%EOF")
