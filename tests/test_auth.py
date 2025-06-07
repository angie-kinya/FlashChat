import pytest
from app import db
from app.models.user import User

class TestAuth:
    def test_register_success(self, client):
        """Test successful user registration"""
        user_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'NewPassword123',
            'display_name': 'New User'
        }
        
        response = client.post('/api/auth/register', json=user_data)
        assert response.status_code == 201
        
        data = response.get_json()
        assert 'access_token' in data
        assert data['user']['username'] == 'newuser'
    
    def test_register_duplicate_username(self, client):
        """Test registration with duplicate username"""
        user_data = {
            'username': 'duplicate',
            'email': 'first@example.com',
            'password': 'Password123',
            'display_name': 'First User'
        }
        
        # First registration
        response = client.post('/api/auth/register', json=user_data)
        assert response.status_code == 201
        
        # Second registration with same username
        user_data['email'] = 'second@example.com'
        response = client.post('/api/auth/register', json=user_data)
        assert response.status_code == 409
        assert 'already exists' in response.get_json()['error']
    
    def test_login_success(self, client):
        """Test successful login"""
        # Register user first
        user_data = {
            'username': 'loginuser',
            'email': 'login@example.com',
            'password': 'LoginPassword123',
            'display_name': 'Login User'
        }
        client.post('/api/auth/register', json=user_data)
        
        # Login
        login_data = {
            'username': 'loginuser',
            'password': 'LoginPassword123'
        }
        
        response = client.post('/api/auth/login', json=login_data)
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'access_token' in data
        assert data['user']['username'] == 'loginuser'
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        login_data = {
            'username': 'nonexistent',
            'password': 'WrongPassword'
        }
        
        response = client.post('/api/auth/login', json=login_data)
        assert response.status_code == 401
        assert 'Invalid credentials' in response.get_json()['error']
    
    def test_get_profile(self, client, auth_headers):
        """Test getting user profile"""
        response = client.get('/api/auth/profile', headers=auth_headers)
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'user' in data
        assert data['user']['username'] == 'testuser'