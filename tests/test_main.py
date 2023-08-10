# tests/test_main.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="module")
def test_client():
    return TestClient(app)

def test_health_checker(test_client):
    response = test_client.get("/api/healthchecker")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to SPOTv2, we are up and running"}

def test_notices_route(test_client):
    response = test_client.get("/api/notices")
    assert response.status_code == 200
