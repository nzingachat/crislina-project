from flask import Blueprint, request, jsonify
from src.models import db, Maintenance, Vehicle
from datetime import datetime, date

maintenance_bp = Blueprint('maintenance', __name__)

@maintenance_bp.route('/maintenance', methods=['GET'])
def get_maintenance_records():
    """Get all maintenance records with optional filtering"""
    try:
        vehicle_id = request.args.get('vehicle_id', type=int)
        maintenance_type = request.args.get('maintenance_type')
        status = request.args.get('status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = Maintenance.query
        
        if vehicle_id:
            query = query.filter(Maintenance.vehicle_id == vehicle_id)
        if maintenance_type:
            query = query.filter(Maintenance.maintenance_type == maintenance_type)
        if status:
            query = query.filter(Maintenance.status == status)
        if start_date:
            try:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                query = query.filter(Maintenance.date >= start_date_obj)
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Invalid start_date format. Use YYYY-MM-DD'
                }), 400
        if end_date:
            try:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                query = query.filter(Maintenance.date <= end_date_obj)
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Invalid end_date format. Use YYYY-MM-DD'
                }), 400
        
        maintenance_records = query.order_by(Maintenance.date.desc()).all()
        return jsonify({
            'success': True,
            'data': [record.to_dict() for record in maintenance_records],
            'count': len(maintenance_records)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching maintenance records: {str(e)}'
        }), 500

@maintenance_bp.route('/maintenance/<int:maintenance_id>', methods=['GET'])
def get_maintenance_record(maintenance_id):
    """Get a specific maintenance record by ID"""
    try:
        maintenance = Maintenance.query.get_or_404(maintenance_id)
        return jsonify({
            'success': True,
            'data': maintenance.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching maintenance record: {str(e)}'
        }), 500

@maintenance_bp.route('/maintenance', methods=['POST'])
def create_maintenance_record():
    """Create a new maintenance record"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['vehicle_id', 'description', 'maintenance_type']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Validate vehicle exists
        vehicle = Vehicle.query.get(data['vehicle_id'])
        if not vehicle:
            return jsonify({
                'success': False,
                'message': 'Vehicle not found'
            }), 404
        
        # Validate maintenance_type
        valid_types = ['routine', 'repair', 'emergency']
        if data['maintenance_type'] not in valid_types:
            return jsonify({
                'success': False,
                'message': f'Invalid maintenance_type. Must be one of: {valid_types}'
            }), 400
        
        # Validate status if provided
        valid_statuses = ['scheduled', 'in_progress', 'completed']
        if 'status' in data and data['status'] not in valid_statuses:
            return jsonify({
                'success': False,
                'message': f'Invalid status. Must be one of: {valid_statuses}'
            }), 400
        
        # Parse date if provided
        maintenance_date = date.today()
        if 'date' in data and data['date']:
            try:
                maintenance_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Invalid date format. Use YYYY-MM-DD'
                }), 400
        
        # Parse next_service_date if provided
        next_service_date = None
        if 'next_service_date' in data and data['next_service_date']:
            try:
                next_service_date = datetime.strptime(data['next_service_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Invalid next_service_date format. Use YYYY-MM-DD'
                }), 400
        
        # Create new maintenance record
        maintenance = Maintenance(
            vehicle_id=data['vehicle_id'],
            date=maintenance_date,
            cost=data.get('cost', 0.0),
            description=data['description'],
            maintenance_type=data['maintenance_type'],
            service_provider=data.get('service_provider'),
            mileage=data.get('mileage'),
            next_service_date=next_service_date,
            status=data.get('status', 'completed')
        )
        
        db.session.add(maintenance)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Maintenance record created successfully',
            'data': maintenance.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error creating maintenance record: {str(e)}'
        }), 500

@maintenance_bp.route('/maintenance/<int:maintenance_id>', methods=['PUT'])
def update_maintenance_record(maintenance_id):
    """Update an existing maintenance record"""
    try:
        maintenance = Maintenance.query.get_or_404(maintenance_id)
        data = request.get_json()
        
        # Validate vehicle if provided
        if 'vehicle_id' in data:
            vehicle = Vehicle.query.get(data['vehicle_id'])
            if not vehicle:
                return jsonify({
                    'success': False,
                    'message': 'Vehicle not found'
                }), 404
        
        # Validate maintenance_type if provided
        if 'maintenance_type' in data:
            valid_types = ['routine', 'repair', 'emergency']
            if data['maintenance_type'] not in valid_types:
                return jsonify({
                    'success': False,
                    'message': f'Invalid maintenance_type. Must be one of: {valid_types}'
                }), 400
        
        # Validate status if provided
        if 'status' in data:
            valid_statuses = ['scheduled', 'in_progress', 'completed']
            if data['status'] not in valid_statuses:
                return jsonify({
                    'success': False,
                    'message': f'Invalid status. Must be one of: {valid_statuses}'
                }), 400
        
        # Update maintenance record fields
        if 'vehicle_id' in data:
            maintenance.vehicle_id = data['vehicle_id']
        if 'date' in data:
            try:
                maintenance.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Invalid date format. Use YYYY-MM-DD'
                }), 400
        if 'cost' in data:
            maintenance.cost = data['cost']
        if 'description' in data:
            maintenance.description = data['description']
        if 'maintenance_type' in data:
            maintenance.maintenance_type = data['maintenance_type']
        if 'service_provider' in data:
            maintenance.service_provider = data['service_provider']
        if 'mileage' in data:
            maintenance.mileage = data['mileage']
        if 'next_service_date' in data:
            if data['next_service_date']:
                try:
                    maintenance.next_service_date = datetime.strptime(data['next_service_date'], '%Y-%m-%d').date()
                except ValueError:
                    return jsonify({
                        'success': False,
                        'message': 'Invalid next_service_date format. Use YYYY-MM-DD'
                    }), 400
            else:
                maintenance.next_service_date = None
        if 'status' in data:
            maintenance.status = data['status']
        
        maintenance.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Maintenance record updated successfully',
            'data': maintenance.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating maintenance record: {str(e)}'
        }), 500

@maintenance_bp.route('/maintenance/<int:maintenance_id>', methods=['DELETE'])
def delete_maintenance_record(maintenance_id):
    """Delete a maintenance record"""
    try:
        maintenance = Maintenance.query.get_or_404(maintenance_id)
        
        db.session.delete(maintenance)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Maintenance record deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error deleting maintenance record: {str(e)}'
        }), 500

@maintenance_bp.route('/maintenance/stats', methods=['GET'])
def get_maintenance_stats():
    """Get maintenance statistics"""
    try:
        vehicle_id = request.args.get('vehicle_id', type=int)
        
        query = Maintenance.query
        if vehicle_id:
            query = query.filter(Maintenance.vehicle_id == vehicle_id)
        
        records = query.all()
        
        total_cost = sum(record.cost for record in records)
        total_records = len(records)
        
        # Group by maintenance type
        type_stats = {}
        for record in records:
            if record.maintenance_type not in type_stats:
                type_stats[record.maintenance_type] = {'count': 0, 'cost': 0}
            type_stats[record.maintenance_type]['count'] += 1
            type_stats[record.maintenance_type]['cost'] += record.cost
        
        # Group by month for trend analysis
        monthly_stats = {}
        for record in records:
            month_key = record.date.strftime('%Y-%m')
            if month_key not in monthly_stats:
                monthly_stats[month_key] = {'count': 0, 'cost': 0}
            monthly_stats[month_key]['count'] += 1
            monthly_stats[month_key]['cost'] += record.cost
        
        stats = {
            'total_cost': total_cost,
            'total_records': total_records,
            'average_cost': total_cost / total_records if total_records > 0 else 0,
            'by_type': type_stats,
            'by_month': monthly_stats
        }
        
        return jsonify({
            'success': True,
            'data': stats
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching maintenance stats: {str(e)}'
        }), 500

