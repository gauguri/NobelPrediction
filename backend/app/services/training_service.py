from app.flows.etl import run_seed_etl
from app.flows.modeling import run_model_training


class TrainingService:
    def run_etl(self) -> str:
        result = run_seed_etl()
        return result

    def train_models(self) -> dict:
        result = run_model_training()
        return result
