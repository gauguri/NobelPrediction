import pytest
from fastapi.testclient import TestClient

import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("SECRET_KEY", "test")

from app.main import app  # noqa: E402


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def test_healthcheck(client):
    response = client.get("/health/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Nobel Prediction API"

