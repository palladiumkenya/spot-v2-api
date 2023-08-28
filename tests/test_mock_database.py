# tests/mock_database.py

class MockFacilityMetrics:
    def __init__(self):
        self._data = [
            {"_id": "1","metric": "Test Metric 1","value": "2", "mfl_code": 123,"created_at": "2023-07-27T17:23:42.721Z", "is_current": True},
            {"_id": "2","metric": "Test Metric 2","value": "1", "mfl_code": 123,"created_at": "2023-07-27T17:23:42.721Z", "is_current": False},
        ]

    def aggregate(self, pipeline):
        return self._data

class MockNotices:
    def __init__(self):
        self._data = [
            {"_id": "1", "rank": 1, "level": 1, "title": "Title 1", "message": "Message 1"},
            {"_id": "2", "rank": 2, "level": 2, "title": "Title 2", "message": "Message 2"},
        ]

    def aggregate(self, pipeline):
        return self._data

