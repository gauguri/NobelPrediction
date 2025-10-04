import shutil
from pathlib import Path

from app.core.config import get_settings
from app.core.database import engine
from app.models.base import Base
from app.models import nobel  # noqa: F401

settings = get_settings()


def bootstrap_state() -> None:
    Base.metadata.create_all(bind=engine)
    seed_source = Path(__file__).resolve().parents[1] / "data" / "seed"
    seed_target = settings.data_dir / "seed"
    if not seed_target.exists():
        seed_target.mkdir(parents=True, exist_ok=True)
    for file in seed_source.glob("*.json"):
        target = seed_target / file.name
        if not target.exists():
            shutil.copy(file, target)
