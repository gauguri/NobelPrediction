# Nobel Prize Prediction Platform

This repository implements a production-oriented, end-to-end platform for forecasting Nobel Prize laureates across Physics, Chemistry, Physiology/Medicine, and Economics. The system is designed according to the requirements in `prompt.md`, covering data ingestion, feature engineering, modeling, evaluation, and a transparent web interface.

## Repository structure

```
backend/        # FastAPI application, SQLAlchemy models, Prefect flows, modeling services
frontend/       # React + Vite + Material UI single-page application
etl/            # Prefect flows and data ingestion utilities
models/         # Training scripts, evaluation reports, model card
infra/          # Docker, Make, CI configuration, bootstrap helpers
notebooks/      # Jupyter notebooks for EDA and model documentation
shared/         # Shared assets (schemas, sample data, expectation suites)
```

## Getting started

### Prerequisites

- Docker & Docker Compose
- Make (GNU make >= 3.81)
- Python 3.11 (for local execution outside Docker)
- Node.js 18+ and pnpm (for local frontend dev)

### Environment

Copy the environment template:

```bash
cp .env.example .env
```

The defaults are tuned for local development. Update secrets (e.g., PostgreSQL password) as needed.

### Bootstrap (toy dataset)

The project ships with a miniature synthetic dataset and pretrained stub models so the full application runs end-to-end without external credentials. To stand up all services, run:

```bash
make bootstrap
```

This command will:

1. Build Docker images.
2. Launch Docker Compose (PostgreSQL, MinIO, backend API, frontend UI).
3. Run the Prefect seed ETL to populate DuckDB staging and PostgreSQL production tables with Physics data.
4. Train baseline models and publish artifacts to `shared/artifacts/`.
5. Load sample predictions into the API database.

After bootstrapping, access:

- API docs: http://localhost:8000/docs
- Frontend UI: http://localhost:5173
- MinIO console: http://localhost:9001 (user/pass from `.env`)

### Development workflows

- **Backend**
  ```bash
  cd backend
  poetry install  # or pip install -r requirements.txt
  poetry run uvicorn app.main:app --reload
  ```

- **Frontend**
  ```bash
  cd frontend
  pnpm install
  pnpm dev
  ```

- **Tests & linting**
  ```bash
  make test
  make lint
  ```

- **Prefect flows**
  ```bash
  cd etl
  poetry run python -m flows.seed_physics_flow
  ```

- **Model training**
  ```bash
  cd models
  poetry run python training/train_baseline.py
  ```

### Reports & exports

The backend exposes:

- `/predictions/{field}` – JSON shortlist for the specified field and horizon.
- `/reports/csv/{field}` – CSV export.
- `/reports/pdf/{field}` – PDF summary generated via ReportLab.
- `/backtests/{field}` – Backtest metrics for 2000-2020 (toy data).

### Data governance

Great Expectations suites live in `shared/great_expectations/`. They are executed during ETL to verify schema, uniqueness, and freshness metadata. The Prefect flow records provenance in PostgreSQL via the `data_provenance` table.

### Model card

See `models/model_card.md` for limitations, ethical considerations, and intended use.

### Continuous Integration

GitHub Actions workflow `.github/workflows/ci.yml` runs linting (ruff, mypy, eslint) and tests (pytest, vitest) on pull requests.

### License

MIT License – see `LICENSE`.

## References

- Fuoco, *How To Predict The Winners Of The Nobel Prize For 2025* (SSRN 5254426).
- Garfield, *Can Nobel Prize Winners Be Predicted?*
- Clarivate Citation Laureates program documentation.
- Chemical & Engineering News expert prediction lists.

