# tests/test_facilities.py
import pytest
from unittest.mock import Mock
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="module")
def test_client():
    return TestClient(app)

def test_update_facilities_route(test_client, monkeypatch):
    # Create a mock function for get_all_facilities
    mock_get_all_facilities = Mock()
    
    # Monkeypatch the get_all_facilities function in your module
    monkeypatch.setattr("app.routers.facilities.get_all_facilities", mock_get_all_facilities)

    response = test_client.get("/api/facilities/update_facilities")
    
    assert response.status_code == 200
    assert response.json() == {"message": "Started Pulling Facilities"}
    
    # Assert that the mock function was called
    mock_get_all_facilities.assert_called_once()

def test_get_facility_by_code(test_client, monkeypatch):
    # Create a mock facility data to simulate database behavior
    mock_facility_data = {
                    "mfl_code": 123, 
                    "subcounty": "subcounty","county": "county",
                    "partner": "partner",
                    "owner": "owner",
                    "agency": "agency",
                    "lat": 0,
                    "lon": 0,
                    "name": "Test Facility"
                }
    
    # Create a mock database query function
    mock_find_one = Mock(return_value=mock_facility_data)
    
    # Monkeypatch the database query function to use the mock
    monkeypatch.setattr("app.database.Facility.find_one", mock_find_one)
    
    # Replace `123` with a valid facility code for your test
    response = test_client.get("/api/facilities/123")
    
    assert response.status_code == 200
    assert response.json() == {"facility": {
                    "mfl_code": 123, 
                    "subcounty": "subcounty","county": "county",
                    "partner": "partner",
                    "owner": "owner",
                    "agency": "agency",
                    "lat": 0,
                    "lon": 0,
                    "name": "Test Facility"
                }}
    mock_find_one.assert_called_once_with({"mfl_code": 123})

# Add more test functions for other routes and scenarios


def test_get_facility_by_invalid_code(test_client):
    # Test for a non-existing facility code
    response = test_client.get("/api/facilities/999")
    assert response.status_code == 404
    # Add assertions or check response content accordingly

