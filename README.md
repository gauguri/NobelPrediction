# Nobel Prediction Platform

A production-ready skeleton that demonstrates how to ingest bibliometric seed data, train a baseline Nobel prize prediction model, and surface transparent shortlists via a FastAPI backend and a React + Material UI frontend.

## Features

- **Automated ETL** using Prefect to hydrate a SQLite store from OpenAlex-inspired seed JSON.
- **Data quality checks** with lightweight Pandas-based expectations before model training.
- **Baseline modeling** with a calibrated logistic-style scoring heuristic implemented in Prefect flows.
- **Explainability** via pseudo-SHAP feature impact summaries.
- **Backtest metrics** surfaced from curated historical results.
- **FastAPI** endpoints for predictions, candidate detail, provenance, and PDF/CSV report exports.
- **React dashboard** with Plotly charts and provenance drawer.
- **Docker Compose** setup for one-command local spin up.
- **pytest** coverage for critical API paths.

## Getting started

### Prerequisites

- Python 3.11
- Node.js 18+
- Docker (optional but recommended)

### Local bootstrap

```bash
make bootstrap
```

This installs dependencies, boots the SQLite schema, runs the seed ETL, trains the baseline model, and saves predictions/reports into `storage/`.

### Running the stack locally

```bash
make docker-up
```

- Backend API: http://localhost:8000
- Frontend UI: http://localhost:5173

Within the UI you can:

1. Inspect the Physics shortlist across horizons.
2. Drill into candidate profiles with provenance metadata.
3. View backtest diagnostics.
4. Trigger CSV/PDF downloads via the "Exports" menu (API endpoints).

### Tests

```bash
make backend-test
```

### Frontend build

```bash
make frontend-build
```

## Repository layout

```
backend/   FastAPI application, Prefect flows, modeling artifacts
frontend/  React + Vite dashboard
storage/   Runtime database, staging data, reports (created on bootstrap)
```

## Configuration

Environment variables are read from `.env` if present. A starter template is provided in `.env.example`.

## References

- Fuoco (2024) — *How To Predict The Winners Of The Nobel Prize For 2025*.
- Garfield (1977) — *Can Nobel Prize Winners Be Predicted?*
- Clarivate Citation Laureates archives.
- ChemistryWorld & C&EN expert shortlists.
