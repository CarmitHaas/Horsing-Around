import pytest
from unittest.mock import MagicMock

# This function will be called before any test is run
@pytest.fixture(autouse=True)
def mock_db_connection(monkeypatch):
    # Create a mock client
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_client.__getitem__.return_value = mock_db

    # Mock the connect_to_mongo function
    def mock_connect_to_mongo(*args, **kwargs):
        return mock_client

    # Apply the mock to your app module
    monkeypatch.setattr('app.connect_to_mongo', mock_connect_to_mongo)
    monkeypatch.setattr('app.client', mock_client)
    monkeypatch.setattr('app.db', mock_db)

@pytest.fixture
def client():
    from app import app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client