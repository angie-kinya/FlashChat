from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.message import Room, Message
from app.models.user import User
from app.utils.auth import jwt_required_with_user
from app.utils.validators import validate_json

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/rooms', methods=['GET'])
@jwt_required_with_user
def get_rooms(current_user):
    """Get all available chat rooms"""
    rooms = Room.query.filter_by(is_private=False).all()
    return jsonify({
        'rooms': [room.to_dict() for room in rooms]
    }), 200

@chat_bp.route('/rooms', methods=['POST'])
@jwt_required_with_user
@validate_json('name')
def create_room(current_user):
    """Create a new chat room"""
    data = request.get_json()
    
    # Check if room name already exists
    if Room.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'Room name already exists'}), 409
    
    room = Room(
        name=data['name'],
        description=data.get('description', ''),
        is_private=data.get('is_private', False),
        created_by=current_user.id
    )
    
    db.session.add(room)
    db.session.commit()
    
    return jsonify({
        'message': 'Room created successfully',
        'room': room.to_dict()
    }), 201

@chat_bp.route('/rooms/<int:room_id>/messages', methods=['GET'])
@jwt_required_with_user
def get_room_messages(current_user, room_id):
    """Get messages for a specific room"""
    room = Room.query.get_or_404(room_id)
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    messages = Message.query.filter_by(room_id=room_id)\
        .order_by(Message.timestamp.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'messages': [msg.to_dict() for msg in reversed(messages.items)],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': messages.total,
            'pages': messages.pages,
            'has_next': messages.has_next,
            'has_prev': messages.has_prev
        }
    }), 200

@chat_bp.route('/rooms/<int:room_id>/messages', methods=['POST'])
@jwt_required_with_user
@validate_json('content')
def send_message(current_user, room_id):
    """Send a message to a room"""
    room = Room.query.get_or_404(room_id)
    data = request.get_json()
    
    message = Message(
        content=data['content'],
        user_id=current_user.id,
        room_id=room_id,
        message_type=data.get('message_type', 'text')
    )
    
    db.session.add(message)
    db.session.commit()
    
    return jsonify({
        'message': 'Message sent successfully',
        'data': message.to_dict()
    }), 201