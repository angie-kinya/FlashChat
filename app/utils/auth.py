from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models.user import User

def jwt_required_with_user(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        return f(current_user, *args, **kwargs)
    return decorated_function