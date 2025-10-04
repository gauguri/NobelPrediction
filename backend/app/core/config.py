from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    app_name: str = "Nobel Prediction API"
    secret_key: str = Field("change-me", env="SECRET_KEY")
    access_token_expire_minutes: int = Field(60, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    postgres_user: str = Field("nobel", env="POSTGRES_USER")
    postgres_password: str = Field("nobel_password", env="POSTGRES_PASSWORD")
    postgres_host: str = Field("postgres", env="POSTGRES_HOST")
    postgres_port: int = Field(5432, env="POSTGRES_PORT")
    postgres_db: str = Field("nobel", env="POSTGRES_DB")
    database_url: str | None = Field(None, env="DATABASE_URL")

    minio_endpoint: str = Field(..., env="MINIO_ENDPOINT")
    minio_root_user: str = Field(..., env="MINIO_ROOT_USER")
    minio_root_password: str = Field(..., env="MINIO_ROOT_PASSWORD")

    prefect_api_url: str = Field("http://prefect:4200/api", env="PREFECT_API_URL")

    openalex_api_key: str | None = Field(None, env="OPENALEX_API_KEY")
    newsapi_key: str | None = Field(None, env="NEWSAPI_KEY")
    gdelt_api_key: str | None = Field(None, env="GDELT_API_KEY")

    allowed_origins: List[str] = Field(default_factory=lambda: ["*"])

    base_dir: Path = Path(__file__).resolve().parent.parent.parent
    shared_dir: Path = base_dir / ".." / "shared"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()

