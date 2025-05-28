import pytest
from unittest.mock import MagicMock, patch
from bson import ObjectId


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


def test_login_invalid_credentials(client):
    response = client.post('/login', data={
        'username': 'wrong',
        'password': 'wrong'
    })
    assert b'Invalid username or password' in response.data


def test_index_page(client):
    response = client.get('/index')
    assert response.status_code == 200


def test_add_horse_requires_login(client):
    response = client.post('/add_horse',
                           json={'name': 'TestHorse', 'image': 'test.jpg'},
                           follow_redirects=False)
    assert response.status_code in (302, 401)


def test_add_chore_requires_login(client):
    response = client.post('/add_chore',
                           json={'name': 'Feed', 'category': 'day_opening'},
                           follow_redirects=False)
    assert response.status_code in (302, 401)


def test_update_chore_requires_login(client):
    response = client.post('/update_chore',
                           json={'horse_id': str(ObjectId()), 'chore_id': str(ObjectId()), 'completed': True},
                           follow_redirects=False)
    assert response.status_code in (302, 401)


def test_remove_horse_requires_login(client):
    response = client.post('/remove_horse',
                           json={'horse_id': str(ObjectId())},
                           follow_redirects=False)
    assert response.status_code in (302, 401)


def test_change_password_requires_login(client):
    response = client.post('/change_password',
                           json={'new_password': 'newpass'},
                           follow_redirects=False)
    assert response.status_code in (302, 401)


def test_metrics_endpoint(client):
    response = client.get('/metrics')
    assert response.status_code == 200
    assert b'total_horses' in response.data


def test_horses_endpoint(client):
    response = client.get('/horses')
    assert response.status_code == 200
