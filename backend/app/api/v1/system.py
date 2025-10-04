from fastapi import APIRouter

from app.services.bootstrap import bootstrap_state

router = APIRouter()


@router.post("/bootstrap")
def bootstrap() -> dict[str, str]:
    bootstrap_state()
    return {"status": "bootstrapped"}
