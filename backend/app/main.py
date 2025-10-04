from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import etl, health, models, predictions, reports
from app.core.config import get_settings
from app.core.database import Base, engine

settings = get_settings()

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name, version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(predictions.router)
app.include_router(etl.router)
app.include_router(models.router)
app.include_router(reports.router)


@app.get("/", tags=["meta"])
def read_root() -> dict[str, str]:
    return {
        "service": settings.app_name,
        "status": "ok",
        "generated_at": datetime.utcnow().isoformat(),
    }

