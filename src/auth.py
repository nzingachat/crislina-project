import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from src.models import User

class AuthManager:
    @staticmethod
    def generate_token(user):
        """Generate JWT token for user"""
        payload = {
            'user_id': user.id,
            'username': user.username,
            'role': user.role,
            'exp': datetime.utcnow() + timedelta(hours=24),  # Token expires in 24 hours
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
        return token
    
    @staticmethod
    def verify_token(token):
        """Verify JWT token and return user data"""
        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    @staticmethod
    def get_current_user():
        """Get current user from request token"""
        token = None
        
        # Check for token in Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return None
        
        if not token:
            return None
        
        payload = AuthManager.verify_token(token)
        if not payload:
            return None
        
        user = User.query.get(payload['user_id'])
        return user

def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        user = AuthManager.get_current_user()
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'Token is missing or invalid'
            }), 401
        
        return f(current_user=user, *args, **kwargs)
    
    return decorated

def role_required(*allowed_roles):
    """Decorator to require specific roles"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = AuthManager.get_current_user()
            
            if not user:
                return jsonify({
                    'success': False,
                    'message': 'Token is missing or invalid'
                }), 401
            
            if user.role not in allowed_roles:
                return jsonify({
                    'success': False,
                    'message': f'Access denied. Required roles: {", ".join(allowed_roles)}'
                }), 403
            
            return f(current_user=user, *args, **kwargs)
        
        return decorated
    return decorator

def admin_required(f):
    """Decorator to require admin role"""
    return role_required('admin')(f)

def admin_or_manager_required(f):
    """Decorator to require admin or manager role"""
    return role_required('admin', 'manager')(f)

