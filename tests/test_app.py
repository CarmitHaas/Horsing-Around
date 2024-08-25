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

def test_404_page(client):
    response = client.get('/nonexistent-page')
    assert response.status_code == 404
    assert b'404' in response.data

def test_login_page(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data

def test_static_file(client):
    response = client.get('/static/css/style.css')
    assert response.status_code == 200
    assert response.content_type == 'text/css; charset=utf-8'