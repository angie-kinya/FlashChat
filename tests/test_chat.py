import pytest
from app import db
from app.models.message import Room, Message

class TestChat:
    def test_create_room(self, client, auth_headers):
        """Test creating a new chat room"""
        room_data = {
            'name': 'Test Room',
            'description': 'A test chat room'
        }
        
        response = client.post('/api/chat/rooms', json=room_data, headers=auth_headers)
        assert response.status_code == 201
        
        data = response.get_json()
        assert data['room']['name'] == 'Test Room'
    
    def test_get_rooms(self, client, auth_headers):
        """Test getting list of rooms"""
        # Create a room first
        room_data = {'name': 'Public Room'}
        client.post('/api/chat/rooms', json=room_data, headers=auth_headers)
        
        response = client.get('/api/chat/rooms', headers=auth_headers)
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'rooms' in data
        assert len(data['rooms']) >= 1
    
    def test_send_message(self, client, auth_headers):
        """Test sending a message to a room"""
        # Create a room first
        room_data = {'name': 'Message Room'}
        room_response = client.post('/api/chat/rooms', json=room_data, headers=auth_headers)
        room_id = room_response.get_json()['room']['id']
        
        # Send message
        message_data = {
            'content': 'Hello, World!'
        }
        
        response = client.post(f'/api/chat/rooms/{room_id}/messages', 
                             json=message_data, headers=auth_headers)
        assert response.status_code == 201
        
        data = response.get_json()
        assert data['data']['content'] == 'Hello, World!'
    
    def test_get_room_messages(self, client, auth_headers):
        """Test getting messages from a room"""
        # Create room and send message
        room_data = {'name': 'Messages Room'}
        room_response = client.post('/api/chat/rooms', json=room_data, headers=auth_headers)
        room_id = room_response.get_json()['room']['id']
        
        message_data = {'content': 'Test message'}
        client.post(f'/api/chat/rooms/{room_id}/messages', 
                   json=message_data, headers=auth_headers)
        
        # Get messages
        response = client.get(f'/api/chat/rooms/{room_id}/messages', headers=auth_headers)
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'messages' in data
        assert len(data['messages']) == 1
        assert data['messages'][0]['content'] == 'Test message'