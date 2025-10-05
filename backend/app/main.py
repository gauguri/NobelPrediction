from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import router as api_router
from app.core.config import get_settings
from app.services.bootstrap import bootstrap_state


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Nobel Prize Prediction API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=settings.api_prefix)

    return app


app = create_app()


@app.on_event("startup")
def on_startup() -> None:
    bootstrap_state()


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}
