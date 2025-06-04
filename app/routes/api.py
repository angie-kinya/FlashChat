from flask import Blueprint, jsonify
from app.models.user import User
from app.models.message import Room

api_bp = Blueprint('api', __name__)

@api_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get application statistics"""
    total_users = User.query.count()
    online_users = User.query.filter_by(is_online=True).count()
    total_rooms = Room.query.count()
    
    return jsonify({
        'total_users': total_users,
        'online_users': online_users,
        'total_rooms': total_rooms
    }), 200