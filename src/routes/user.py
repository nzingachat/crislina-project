from flask import Blueprint, request, jsonify
from src.models import db, User
from src.auth import AuthManager, token_required, admin_required
from datetime import datetime

user_bp = Blueprint('user', __name__)

@user_bp.route('/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Validate role if provided
        valid_roles = ['admin', 'manager', 'driver']
        role = data.get('role', 'driver')
        if role not in valid_roles:
            return jsonify({
                'success': False,
                'message': f'Invalid role. Must be one of: {valid_roles}'
            }), 400
        
        # Check if username already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({
                'success': False,
                'message': 'Username already exists'
            }), 400
        
        # Check if email already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({
                'success': False,
                'message': 'Email already exists'
            }), 400
        
        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            role=role
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Generate token
        token = AuthManager.generate_token(user)
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'data': {
                'user': user.to_dict(),
                'token': token
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error registering user: {str(e)}'
        }), 500

@user_bp.route('/auth/login', methods=['POST'])
def login():
    """Login user and return JWT token"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('username') or not data.get('password'):
            return jsonify({
                'success': False,
                'message': 'Username and password are required'
            }), 400
        
        # Find user
        user = User.query.filter_by(username=data['username']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({
                'success': False,
                'message': 'Invalid username or password'
            }), 401
        
        if not user.is_active:
            return jsonify({
                'success': False,
                'message': 'Account is deactivated'
            }), 401
        
        # Generate token
        token = AuthManager.generate_token(user)
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'data': {
                'user': user.to_dict(),
                'token': token
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error during login: {str(e)}'
        }), 500

@user_bp.route('/auth/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    """Get current user information"""
    return jsonify({
        'success': True,
        'data': current_user.to_dict()
    }), 200

@user_bp.route('/auth/change-password', methods=['POST'])
@token_required
def change_password(current_user):
    """Change user password"""
    try:
        data = request.get_json()
        
        if not data.get('current_password') or not data.get('new_password'):
            return jsonify({
                'success': False,
                'message': 'Current password and new password are required'
            }), 400
        
        if not current_user.check_password(data['current_password']):
            return jsonify({
                'success': False,
                'message': 'Current password is incorrect'
            }), 400
        
        current_user.set_password(data['new_password'])
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Password changed successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error changing password: {str(e)}'
        }), 500

@user_bp.route('/users', methods=['GET'])
@admin_required
def get_users(current_user):
    """Get all users (admin only)"""
    try:
        users = User.query.all()
        return jsonify({
            'success': True,
            'data': [user.to_dict() for user in users],
            'count': len(users)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching users: {str(e)}'
        }), 500

@user_bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id, current_user):
    """Get a specific user by ID (admin only)"""
    try:
        user = User.query.get_or_404(user_id)
        return jsonify({
            'success': True,
            'data': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching user: {str(e)}'
        }), 500

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id, current_user):
    """Update a user (admin only)"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        # Validate role if provided
        if 'role' in data:
            valid_roles = ['admin', 'manager', 'driver']
            if data['role'] not in valid_roles:
                return jsonify({
                    'success': False,
                    'message': f'Invalid role. Must be one of: {valid_roles}'
                }), 400
        
        # Check if new username already exists (if being changed)
        if 'username' in data and data['username'] != user.username:
            existing_user = User.query.filter_by(username=data['username']).first()
            if existing_user:
                return jsonify({
                    'success': False,
                    'message': 'Username already exists'
                }), 400
        
        # Check if new email already exists (if being changed)
        if 'email' in data and data['email'] != user.email:
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user:
                return jsonify({
                    'success': False,
                    'message': 'Email already exists'
                }), 400
        
        # Update user fields
        if 'username' in data:
            user.username = data['username']
        if 'email' in data:
            user.email = data['email']
        if 'role' in data:
            user.role = data['role']
        if 'is_active' in data:
            user.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'User updated successfully',
            'data': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating user: {str(e)}'
        }), 500

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id, current_user):
    """Delete a user (admin only)"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Prevent admin from deleting themselves
        if user.id == current_user.id:
            return jsonify({
                'success': False,
                'message': 'Cannot delete your own account'
            }), 400
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'User deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error deleting user: {str(e)}'
        }), 500

