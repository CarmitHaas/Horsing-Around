import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
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

def test_invalid_login(client):
    response = client.post('/login', data=dict(
        username='invalid',
        password='invalid'
    ), follow_redirects=True)
    assert b'Invalid username or password' in response.data

