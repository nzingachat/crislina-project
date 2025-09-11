from flask import Blueprint, request, jsonify
from src.models import db, Vehicle
from src.auth import token_required, admin_required, admin_or_manager_required
from datetime import datetime

vehicle_bp = Blueprint('vehicle', __name__)

@vehicle_bp.route('/vehicles', methods=['GET'])
@token_required
def get_vehicles(current_user):
    """Get all vehicles with optional filtering"""
    try:
        status = request.args.get('status')
        fuel_type = request.args.get('fuel_type')
        
        query = Vehicle.query
        
        if status:
            query = query.filter(Vehicle.status == status)
        if fuel_type:
            query = query.filter(Vehicle.fuel_type == fuel_type)
            
        vehicles = query.all()
        return jsonify({
            'success': True,
            'data': [vehicle.to_dict() for vehicle in vehicles],
            'count': len(vehicles)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching vehicles: {str(e)}'
        }), 500

@vehicle_bp.route('/vehicles/<int:vehicle_id>', methods=['GET'])
@token_required
def get_vehicle(vehicle_id, current_user):
    """Get a specific vehicle by ID"""
    try:
        vehicle = Vehicle.query.get_or_404(vehicle_id)
        return jsonify({
            'success': True,
            'data': vehicle.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching vehicle: {str(e)}'
        }), 500

@vehicle_bp.route('/vehicles', methods=['POST'])
@admin_or_manager_required
def create_vehicle(current_user):
    """Create a new vehicle (admin/manager only)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['reg_no', 'model', 'fuel_type']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Validate fuel_type
        valid_fuel_types = ['petrol', 'diesel', 'electric']
        if data['fuel_type'] not in valid_fuel_types:
            return jsonify({
                'success': False,
                'message': f'Invalid fuel_type. Must be one of: {valid_fuel_types}'
            }), 400
        
        # Validate status if provided
        valid_statuses = ['active', 'maintenance', 'inactive']
        if 'status' in data and data['status'] not in valid_statuses:
            return jsonify({
                'success': False,
                'message': f'Invalid status. Must be one of: {valid_statuses}'
            }), 400
        
        # Check if registration number already exists
        existing_vehicle = Vehicle.query.filter_by(reg_no=data['reg_no']).first()
        if existing_vehicle:
            return jsonify({
                'success': False,
                'message': 'Vehicle with this registration number already exists'
            }), 400
        
        # Create new vehicle
        vehicle = Vehicle(
            reg_no=data['reg_no'],
            model=data['model'],
            fuel_type=data['fuel_type'],
            status=data.get('status', 'active')
        )
        
        db.session.add(vehicle)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Vehicle created successfully',
            'data': vehicle.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error creating vehicle: {str(e)}'
        }), 500

@vehicle_bp.route('/vehicles/<int:vehicle_id>', methods=['PUT'])
@admin_or_manager_required
def update_vehicle(vehicle_id, current_user):
    """Update an existing vehicle (admin/manager only)"""
    try:
        vehicle = Vehicle.query.get_or_404(vehicle_id)
        data = request.get_json()
        
        # Validate fuel_type if provided
        if 'fuel_type' in data:
            valid_fuel_types = ['petrol', 'diesel', 'electric']
            if data['fuel_type'] not in valid_fuel_types:
                return jsonify({
                    'success': False,
                    'message': f'Invalid fuel_type. Must be one of: {valid_fuel_types}'
                }), 400
        
        # Validate status if provided
        if 'status' in data:
            valid_statuses = ['active', 'maintenance', 'inactive']
            if data['status'] not in valid_statuses:
                return jsonify({
                    'success': False,
                    'message': f'Invalid status. Must be one of: {valid_statuses}'
                }), 400
        
        # Check if new registration number already exists (if being changed)
        if 'reg_no' in data and data['reg_no'] != vehicle.reg_no:
            existing_vehicle = Vehicle.query.filter_by(reg_no=data['reg_no']).first()
            if existing_vehicle:
                return jsonify({
                    'success': False,
                    'message': 'Vehicle with this registration number already exists'
                }), 400
        
        # Update vehicle fields
        if 'reg_no' in data:
            vehicle.reg_no = data['reg_no']
        if 'model' in data:
            vehicle.model = data['model']
        if 'fuel_type' in data:
            vehicle.fuel_type = data['fuel_type']
        if 'status' in data:
            vehicle.status = data['status']
        
        vehicle.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Vehicle updated successfully',
            'data': vehicle.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating vehicle: {str(e)}'
        }), 500

@vehicle_bp.route('/vehicles/<int:vehicle_id>', methods=['DELETE'])
@admin_required
def delete_vehicle(vehicle_id, current_user):
    """Delete a vehicle (admin only)"""
    try:
        vehicle = Vehicle.query.get_or_404(vehicle_id)
        
        # Check if vehicle has associated trips
        if vehicle.trips:
            return jsonify({
                'success': False,
                'message': 'Cannot delete vehicle with associated trips'
            }), 400
        
        db.session.delete(vehicle)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Vehicle deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error deleting vehicle: {str(e)}'
        }), 500

@vehicle_bp.route('/vehicles/<int:vehicle_id>/stats', methods=['GET'])
@token_required
def get_vehicle_stats(vehicle_id, current_user):
    """Get statistics for a specific vehicle"""
    try:
        vehicle = Vehicle.query.get_or_404(vehicle_id)
        
        stats = {
            'total_trips': vehicle.get_total_trips(),
            'total_distance': vehicle.get_total_distance(),
            'total_fuel_used': vehicle.get_total_fuel_used(),
            'maintenance_count': len(vehicle.maintenance_records),
            'total_maintenance_cost': sum(m.cost for m in vehicle.maintenance_records)
        }
        
        return jsonify({
            'success': True,
            'data': stats
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching vehicle stats: {str(e)}'
        }), 500

