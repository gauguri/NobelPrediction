from __future__ import annotations

from app.services.etl import run_seed_flow
from app.services.modeling import train_models, update_predictions_from_artifacts


def main() -> None:
    run_seed_flow()
    train_models()
    update_predictions_from_artifacts()


if __name__ == "__main__":
    main()

