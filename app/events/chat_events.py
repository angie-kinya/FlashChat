from flask import request
from flask_socketio import emit, join_room, leave_room, disconnect
from flask_jwt_extended import decode_token
from app import db, redis_client
from app.models.user import User
from app.models.message import Message, Room
import json
from datetime import datetime

def register_events(socketio):
    
    @socketio.on('connect')
    def handle_connect(auth):
        """Handle client connection"""
        try:
            # Verify JWT token
            if not auth or 'token' not in auth:
                disconnect()
                return False
            
            token_data = decode_token(auth['token'])
            user_id = token_data['sub']
            user = User.query.get(user_id)
            
            if not user:
                disconnect()
                return False
            
            # Store user session
            redis_client.hset(f'user_session:{request.sid}', mapping={
                'user_id': user_id,
                'username': user.username,
                'display_name': user.display_name
            })
            
            # Update user status
            user.is_online = True
            db.session.commit()
            
            emit('connected', {'message': f'Welcome, {user.display_name}!'})
            
        except Exception as e:
            print(f"Connection error: {e}")
            disconnect()
            return False
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        try:
            # Get user session
            session_data = redis_client.hgetall(f'user_session:{request.sid}')
            if session_data:
                user_id = session_data.get(b'user_id') or session_data.get('user_id')
                if user_id:
                    user = User.query.get(int(user_id))
                    if user:
                        user.is_online = False
                        user.update_last_seen()
            
            # Clean up session
            redis_client.delete(f'user_session:{request.sid}')
            
        except Exception as e:
            print(f"Disconnect error: {e}")
    
    @socketio.on('join_room')
    def handle_join_room(data):
        """Handle user joining a room"""
        try:
            session_data = redis_client.hgetall(f'user_session:{request.sid}')
            if not session_data:
                emit('error', {'message': 'Invalid session'})
                return
            
            room_id = str(data['room_id'])
            username = (session_data.get(b'username') or session_data.get('username')).decode() if isinstance(session_data.get(b'username') or session_data.get('username'), bytes) else session_data.get(b'username') or session_data.get('username')
            
            # Verify room exists
            room = Room.query.get(int(room_id))
            if not room:
                emit('error', {'message': 'Room not found'})
                return
            
            join_room(room_id)
            
            # Notify room about new user
            emit('user_joined', {
                'username': username,
                'message': f'{username} joined the room',
                'timestamp': datetime.utcnow().isoformat()
            }, room=room_id)
            
            emit('room_joined', {'room_id': room_id, 'room_name': room.name})
            
        except Exception as e:
            emit('error', {'message': f'Error joining room: {str(e)}'})
    
    @socketio.on('leave_room')
    def handle_leave_room(data):
        """Handle user leaving a room"""
        try:
            session_data = redis_client.hgetall(f'user_session:{request.sid}')
            if not session_data:
                return
            
            room_id = str(data['room_id'])
            username = (session_data.get(b'username') or session_data.get('username')).decode() if isinstance(session_data.get(b'username') or session_data.get('username'), bytes) else session_data.get(b'username') or session_data.get('username')
            
            leave_room(room_id)
            
            # Notify room about user leaving
            emit('user_left', {
                'username': username,
                'message': f'{username} left the room',
                'timestamp': datetime.utcnow().isoformat()
            }, room=room_id)
            
        except Exception as e:
            emit('error', {'message': f'Error leaving room: {str(e)}'})
    
    @socketio.on('send_message')
    def handle_message(data):
        """Handle sending a message"""
        try:
            session_data = redis_client.hgetall(f'user_session:{request.sid}')
            if not session_data:
                emit('error', {'message': 'Invalid session'})
                return
            
            user_id = int(session_data.get(b'user_id') or session_data.get('user_id'))
            room_id = data['room_id']
            content = data['content'].strip()
            
            if not content:
                emit('error', {'message': 'Message cannot be empty'})
                return
            
            # Create and save message
            message = Message(
                content=content,
                user_id=user_id,
                room_id=room_id
            )
            
            db.session.add(message)
            db.session.commit()
            
            # Broadcast message to room
            emit('message', message.to_dict(), room=str(room_id))
            
        except Exception as e:
            emit('error', {'message': f'Error sending message: {str(e)}'})
    
    @socketio.on('typing')
    def handle_typing(data):
        """Handle typing indicator"""
        try:
            session_data = redis_client.hgetall(f'user_session:{request.sid}')
            if not session_data:
                return
            
            room_id = str(data['room_id'])
            username = (session_data.get(b'username') or session_data.get('username')).decode() if isinstance(session_data.get(b'username') or session_data.get('username'), bytes) else session_data.get(b'username') or session_data.get('username')
            is_typing = data.get('is_typing', False)
            
            # Broadcast typing status to room (excluding sender)
            emit('typing', {
                'username': username,
                'is_typing': is_typing
            }, room=room_id, include_self=False)
            
        except Exception as e:
            print(f"Typing error: {e}")