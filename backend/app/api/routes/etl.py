from fastapi import APIRouter

from app.services.etl import run_seed_flow

router = APIRouter(prefix="/etl", tags=["etl"])


@router.post("/seed")
def trigger_seed_flow() -> dict[str, str]:
    flow_run_id = run_seed_flow()
    return {"status": "triggered", "flow_run_id": flow_run_id}

