import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.bootstrap import bootstrap_state
from app.services.training_service import TrainingService


client = TestClient(app)


def setup_module(module):
    bootstrap_state()
    service = TrainingService()
    service.run_etl()
    service.train_models()


def test_health():
    response = client.get("/health")
    assert response.status_code == 200


@pytest.mark.parametrize(
    "field",
    ["Physics", "Chemistry", "Medicine", "Literature", "Peace", "Economics"],
)
def test_shortlist_endpoint(field):
    response = client.get(
        "/api/v1/predictions/shortlist", params={"field": field, "horizon": "one_year"}
    )
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert payload
    assert payload[0]["candidate_name"]


def test_shortlist_excludes_laureates():
    response = client.get(
        "/api/v1/predictions/shortlist", params={"field": "Physics", "horizon": "one_year"}
    )
    assert response.status_code == 200
    payload = response.json()
    laureates = [entry for entry in payload if entry["candidate_name"] == "Hiroshi Amano"]
    assert not laureates


def test_reports_generation(tmp_path):
    response = client.get("/api/v1/reports/shortlist.csv", params={"field": "Physics", "horizon": "one_year"})
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")

    response = client.get("/api/v1/reports/shortlist.pdf", params={"field": "Physics", "horizon": "one_year"})
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/pdf")
