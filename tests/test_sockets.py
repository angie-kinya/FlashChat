import pytest
from flask_socketio import SocketIOTestClient
import socketio

import app

def test_websocket_connection():
    socketio_client = SocketIOTestClient(app, socketio)
    
    # Test connection
    received = socketio_client.get_received()
    assert len(received) == 0
    
def test_join_room_event():
    socketio_client = SocketIOTestClient(app, socketio)
    
    # Emit join_room event
    socketio_client.emit('join_room', {'room_id': 1, 'token': 'valid_token'})
    
    # Check for acknowledgment
    received = socketio_client.get_received()
    assert len(received) > 0

def test_send_message_event():
    socketio_client = SocketIOTestClient(app, socketio)
    
    # Join room first
    socketio_client.emit('join_room', {'room_id': 1, 'token': 'valid_token'})
    
    # Send message
    socketio_client.emit('send_message', {
        'room_id': 1,
        'content': 'Hello World',
        'token': 'valid_token'
    })
    
    # Verify message was broadcast
    received = socketio_client.get_received()
    message_events = [r for r in received if r['name'] == 'message']
    assert len(message_events) > 0