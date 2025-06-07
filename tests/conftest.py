import pytest
import os
import tempfile
from app import create_app, db
from app.models.user import User
from app.models.message import Room, Message

@pytest.fixture
def app():
    """Create application for testing"""
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app('testing')
    app.config['DATABASE_URL'] = f'sqlite:///{db_path}'
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create test CLI runner"""
    return app.test_cli_runner()

@pytest.fixture
def auth_headers(client):
    """Create authenticated user and return auth headers"""
    # Create test user
    user_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'TestPassword123',
        'display_name': 'Test User'
    }
    
    response = client.post('/api/auth/register', json=user_data)
    token = response.get_json()['access_token']
    
    return {'Authorization': f'Bearer {token}'}