from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app
from tests.test_mock_database import MockNotices 

client = TestClient(app)

@patch("app.database.Notices", new_callable=MockNotices)
def test_get_notices(test_client):
    response = client.get("/api/notices/")
    
    assert response.status_code == 200
