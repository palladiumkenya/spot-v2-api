from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app
from tests.test_mock_database import MockFacilityMetrics 

client = TestClient(app)

@patch("app.database.FacilityMetrics", new_callable=MockFacilityMetrics)
def test_get_facility_metrics(test_client):
    response = client.get("/api/metrics/123")
    
    assert response.status_code == 200
