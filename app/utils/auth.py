from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models.user import User

def jwt_required_with_user(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print("jwt_required_with_user: Verifying JWT")
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        print(f"jwt_required_with_user: Current user id: {current_user_id}")
        current_user = User.query.get(current_user_id)
        if not current_user:
            print("jwt_required_with_user: User not found")
            return jsonify({'error': 'User not found'}), 404
        return f(current_user, *args, **kwargs)
    return decorated_function
