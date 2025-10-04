.PHONY: bootstrap backend-install frontend-install backend-test frontend-build lint docker-up docker-down

lint:
	cd frontend && npm run lint
	cd backend && poetry run python -m compileall app

bootstrap: backend-install frontend-install
	mkdir -p storage/data storage/models
	poetry -C backend run python -c "from app.services.bootstrap import bootstrap_state; bootstrap_state()"
	poetry -C backend run python -c "from app.services.training_service import TrainingService; s=TrainingService(); s.run_etl(); s.train_models()"

backend-install:
	cd backend && poetry install

frontend-install:
	cd frontend && npm install

backend-test:
	cd backend && poetry run pytest

frontend-build:
	cd frontend && npm run build

docker-up:
	docker compose up --build

docker-down:
	docker compose down
