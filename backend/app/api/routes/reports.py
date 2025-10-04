from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.reports import build_csv_report, build_pdf_report

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/csv/{field}")
def download_csv(field: str, horizon: str = "one_year", db: Session = Depends(get_db)) -> FileResponse:
    path = build_csv_report(field=field, horizon=horizon, db=db)
    if path is None:
        raise HTTPException(status_code=404, detail="No predictions available")
    return FileResponse(path=path, media_type="text/csv", filename=f"{field}_{horizon}_shortlist.csv")


@router.get("/pdf/{field}")
def download_pdf(field: str, horizon: str = "one_year", db: Session = Depends(get_db)) -> FileResponse:
    path = build_pdf_report(field=field, horizon=horizon, db=db)
    if path is None:
        raise HTTPException(status_code=404, detail="No predictions available")
    return FileResponse(path=path, media_type="application/pdf", filename=f"{field}_{horizon}_shortlist.pdf")

