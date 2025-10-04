from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.reports.generators import generate_csv_report, generate_pdf_report

router = APIRouter()


@router.get("/shortlist.csv")
def shortlist_csv(field: str, horizon: str = "one_year"):
    file_path = generate_csv_report(field=field, horizon=horizon)
    return FileResponse(path=file_path, media_type="text/csv", filename=file_path.name)


@router.get("/shortlist.pdf")
def shortlist_pdf(field: str, horizon: str = "one_year"):
    file_path = generate_pdf_report(field=field, horizon=horizon)
    return FileResponse(path=file_path, media_type="application/pdf", filename=file_path.name)
