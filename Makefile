SHELL := /bin/bash

.PHONY: bootstrap up down logs lint test format data train frontend backend etl

bootstrap: ## Build images, start stack, seed data, train models
cp -n .env.example .env || true
docker compose up --build -d
docker compose exec backend poetry run python -m app.workflows.bootstrap

up: ## Start docker compose stack
docker compose up -d
docker compose logs -f

down: ## Stop stack and remove containers
docker compose down -v

logs: ## Tail backend logs
docker compose logs -f backend

lint: ## Run linting across services
cd backend && poetry run ruff check app && poetry run mypy app
cd frontend && pnpm lint

format: ## Autoformat code
cd backend && poetry run ruff format app && poetry run isort app
cd frontend && pnpm format

test: ## Run backend and frontend tests
cd backend && poetry run pytest
cd frontend && pnpm test -- --run

train: ## Train models locally
cd models && poetry run python training/train_baseline.py

backend: ## Run backend locally
cd backend && poetry run uvicorn app.main:app --reload

frontend: ## Run frontend locally
cd frontend && pnpm dev

etl: ## Execute Prefect seed flow
cd etl && poetry run python -m flows.seed_physics_flow

