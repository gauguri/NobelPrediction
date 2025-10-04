from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    api_prefix: str = "/api"
    cors_origins: List[str] = Field(default_factory=lambda: ["http://localhost:5173"])
    database_url: str = Field(
        default_factory=lambda: f"sqlite:///{Path(__file__).resolve().parents[2] / 'storage' / 'nobel.db'}"
    )
    data_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parents[2] / "storage" / "data")
    model_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parents[2] / "storage" / "models")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.model_dir.mkdir(parents=True, exist_ok=True)
    settings.data_dir.joinpath("predictions").mkdir(parents=True, exist_ok=True)
    return settings
