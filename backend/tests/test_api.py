import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.training_service import TrainingService


@pytest.fixture(scope="module")
def client() -> TestClient:
    with TestClient(app) as test_client:
        service = TrainingService()
        service.run_etl()
        service.train_models()
        yield test_client


def test_health(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200


@pytest.mark.parametrize(
    "field",
    ["Physics", "Chemistry", "Medicine", "Literature", "Peace", "Economics"],
)
def test_shortlist_endpoint(client: TestClient, field: str):
    response = client.get(
        "/api/v1/predictions/shortlist", params={"field": field, "horizon": "one_year"}
    )
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert payload
    assert payload[0]["candidate_name"]


def test_shortlist_excludes_laureates(client: TestClient):
    response = client.get(
        "/api/v1/predictions/shortlist", params={"field": "Physics", "horizon": "one_year"}
    )
    assert response.status_code == 200
    payload = response.json()
    laureates = [entry for entry in payload if entry["candidate_name"] == "Hiroshi Amano"]
    assert not laureates


def test_reports_generation(client: TestClient, tmp_path):
    response = client.get(
        "/api/v1/reports/shortlist.csv", params={"field": "Physics", "horizon": "one_year"}
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")

    response = client.get(
        "/api/v1/reports/shortlist.pdf", params={"field": "Physics", "horizon": "one_year"}
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/pdf")


def test_backtests_bootstrapped(client: TestClient):
    response = client.get("/api/v1/predictions/backtests")
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert payload
