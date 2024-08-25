import pytest
from mock import patch, MagicMock

# Patch the connect_to_mongo function before importing app
mock_client = MagicMock()
with patch('app.connect_to_mongo', return_value=mock_client):
    from app import app, db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    with app.test_client() as client:
        yield client

def test_welcome_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome to Horsing Around' in response.data

def test_login_page(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data

def test_404_page(client):
    response = client.get('/nonexistent-page')
    assert response.status_code == 404
    assert b'404' in response.data

def test_convert_objectid():
    from app import convert_objectid
    from bson import ObjectId

    # Test with a simple dictionary
    test_dict = {'_id': ObjectId('5f50c31e8d6bde1ef5b9a5d8'), 'name': 'Test'}
    result = convert_objectid(test_dict)
    assert isinstance(result['_id'], str)
    assert result['_id'] == '5f50c31e8d6bde1ef5b9a5d8'

    # Test with a nested structure
    test_nested = {
        'horses': [
            {'_id': ObjectId('5f50c31e8d6bde1ef5b9a5d9'), 'name': 'Horse1'},
            {'_id': ObjectId('5f50c31e8d6bde1ef5b9a5da'), 'name': 'Horse2'}
        ]
    }
    result = convert_objectid(test_nested)
    assert isinstance(result['horses'][0]['_id'], str)
    assert isinstance(result['horses'][1]['_id'], str)

def test_user_model():
    from app import User
    user = User('testuser')
    assert user.username == 'testuser'
    assert user.get_id() == 'testuser'