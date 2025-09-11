from flask import Blueprint, request, jsonify
from src.models import db, Driver
from src.auth import token_required, admin_required, admin_or_manager_required
from datetime import datetime

driver_bp = Blueprint('driver', __name__)

@driver_bp.route('/drivers', methods=['GET'])
def get_drivers():
    """Get all drivers with optional filtering"""
    try:
        status = request.args.get('status')
        
        query = Driver.query
        
        if status:
            query = query.filter(Driver.status == status)
            
        drivers = query.all()
        return jsonify({
            'success': True,
            'data': [driver.to_dict() for driver in drivers],
            'count': len(drivers)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching drivers: {str(e)}'
        }), 500

@driver_bp.route('/drivers/<int:driver_id>', methods=['GET'])
def get_driver(driver_id):
    """Get a specific driver by ID"""
    try:
        driver = Driver.query.get_or_404(driver_id)
        return jsonify({
            'success': True,
            'data': driver.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching driver: {str(e)}'
        }), 500

@driver_bp.route('/drivers', methods=['POST'])
def create_driver():
    """Create a new driver"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'license_no']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Validate status if provided
        valid_statuses = ['active', 'inactive']
        if 'status' in data and data['status'] not in valid_statuses:
            return jsonify({
                'success': False,
                'message': f'Invalid status. Must be one of: {valid_statuses}'
            }), 400
        
        # Check if license number already exists
        existing_driver = Driver.query.filter_by(license_no=data['license_no']).first()
        if existing_driver:
            return jsonify({
                'success': False,
                'message': 'Driver with this license number already exists'
            }), 400
        
        # Create new driver
        driver = Driver(
            name=data['name'],
            license_no=data['license_no'],
            phone=data.get('phone'),
            email=data.get('email'),
            status=data.get('status', 'active'),
            user_id=data.get('user_id')
        )
        
        db.session.add(driver)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Driver created successfully',
            'data': driver.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error creating driver: {str(e)}'
        }), 500

@driver_bp.route('/drivers/<int:driver_id>', methods=['PUT'])
def update_driver(driver_id):
    """Update an existing driver"""
    try:
        driver = Driver.query.get_or_404(driver_id)
        data = request.get_json()
        
        # Validate status if provided
        if 'status' in data:
            valid_statuses = ['active', 'inactive']
            if data['status'] not in valid_statuses:
                return jsonify({
                    'success': False,
                    'message': f'Invalid status. Must be one of: {valid_statuses}'
                }), 400
        
        # Check if new license number already exists (if being changed)
        if 'license_no' in data and data['license_no'] != driver.license_no:
            existing_driver = Driver.query.filter_by(license_no=data['license_no']).first()
            if existing_driver:
                return jsonify({
                    'success': False,
                    'message': 'Driver with this license number already exists'
                }), 400
        
        # Update driver fields
        if 'name' in data:
            driver.name = data['name']
        if 'license_no' in data:
            driver.license_no = data['license_no']
        if 'phone' in data:
            driver.phone = data['phone']
        if 'email' in data:
            driver.email = data['email']
        if 'status' in data:
            driver.status = data['status']
        if 'user_id' in data:
            driver.user_id = data['user_id']
        
        driver.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Driver updated successfully',
            'data': driver.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating driver: {str(e)}'
        }), 500

@driver_bp.route('/drivers/<int:driver_id>', methods=['DELETE'])
def delete_driver(driver_id):
    """Delete a driver"""
    try:
        driver = Driver.query.get_or_404(driver_id)
        
        # Check if driver has associated trips
        if driver.trips:
            return jsonify({
                'success': False,
                'message': 'Cannot delete driver with associated trips'
            }), 400
        
        db.session.delete(driver)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Driver deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error deleting driver: {str(e)}'
        }), 500

@driver_bp.route('/drivers/<int:driver_id>/stats', methods=['GET'])
def get_driver_stats(driver_id):
    """Get statistics for a specific driver"""
    try:
        driver = Driver.query.get_or_404(driver_id)
        
        stats = {
            'total_trips': driver.get_total_trips(),
            'total_distance': driver.get_total_distance(),
            'total_fuel_used': driver.get_total_fuel_used()
        }
        
        return jsonify({
            'success': True,
            'data': stats
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching driver stats: {str(e)}'
        }), 500

