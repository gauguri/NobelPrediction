from datetime import datetime
from pathlib import Path
import sys

from app.core.config import get_settings

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

try:
    from etl.flows.seed_physics_flow import seed_physics_flow
except ModuleNotFoundError as exc:  # pragma: no cover
    raise ImportError("Ensure the etl package is available in PYTHONPATH") from exc


def run_seed_flow() -> str:
    """Execute the Prefect flow that builds the toy Physics dataset."""
    get_settings()  # Ensure environment is loaded
    result = seed_physics_flow()
    if isinstance(result, dict) and result.get("status") != "completed":
        raise RuntimeError("Seed flow returned unsuccessful status")

    flow_run_id = f"seed-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    return flow_run_id

