from flask import Blueprint, request, jsonify
from src.models import db, Trip, Vehicle, Driver
from datetime import datetime, date

trip_bp = Blueprint('trip', __name__)

@trip_bp.route('/trips', methods=['GET'])
def get_trips():
    """Get all trips with optional filtering"""
    try:
        vehicle_id = request.args.get('vehicle_id', type=int)
        driver_id = request.args.get('driver_id', type=int)
        status = request.args.get('status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = Trip.query
        
        if vehicle_id:
            query = query.filter(Trip.vehicle_id == vehicle_id)
        if driver_id:
            query = query.filter(Trip.driver_id == driver_id)
        if status:
            query = query.filter(Trip.status == status)
        if start_date:
            try:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                query = query.filter(Trip.trip_date >= start_date_obj)
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Invalid start_date format. Use YYYY-MM-DD'
                }), 400
        if end_date:
            try:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                query = query.filter(Trip.trip_date <= end_date_obj)
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Invalid end_date format. Use YYYY-MM-DD'
                }), 400
        
        trips = query.order_by(Trip.trip_date.desc()).all()
        return jsonify({
            'success': True,
            'data': [trip.to_dict() for trip in trips],
            'count': len(trips)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching trips: {str(e)}'
        }), 500

@trip_bp.route('/trips/<int:trip_id>', methods=['GET'])
def get_trip(trip_id):
    """Get a specific trip by ID"""
    try:
        trip = Trip.query.get_or_404(trip_id)
        return jsonify({
            'success': True,
            'data': trip.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching trip: {str(e)}'
        }), 500

@trip_bp.route('/trips', methods=['POST'])
def create_trip():
    """Create a new trip"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['vehicle_id', 'driver_id', 'source', 'destination']
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
        
        # Validate driver exists
        driver = Driver.query.get(data['driver_id'])
        if not driver:
            return jsonify({
                'success': False,
                'message': 'Driver not found'
            }), 404
        
        # Validate status if provided
        valid_statuses = ['planned', 'in_progress', 'completed', 'cancelled']
        if 'status' in data and data['status'] not in valid_statuses:
            return jsonify({
                'success': False,
                'message': f'Invalid status. Must be one of: {valid_statuses}'
            }), 400
        
        # Parse trip_date if provided
        trip_date = date.today()
        if 'trip_date' in data and data['trip_date']:
            try:
                trip_date = datetime.strptime(data['trip_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Invalid trip_date format. Use YYYY-MM-DD'
                }), 400
        
        # Parse start_time and end_time if provided
        start_time = None
        end_time = None
        if 'start_time' in data and data['start_time']:
            try:
                start_time = datetime.fromisoformat(data['start_time'])
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Invalid start_time format. Use ISO format'
                }), 400
        
        if 'end_time' in data and data['end_time']:
            try:
                end_time = datetime.fromisoformat(data['end_time'])
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Invalid end_time format. Use ISO format'
                }), 400
        
        # Create new trip
        trip = Trip(
            vehicle_id=data['vehicle_id'],
            driver_id=data['driver_id'],
            source=data['source'],
            destination=data['destination'],
            distance=data.get('distance'),
            fuel_used=data.get('fuel_used'),
            trip_date=trip_date,
            start_time=start_time,
            end_time=end_time,
            status=data.get('status', 'planned'),
            notes=data.get('notes')
        )
        
        db.session.add(trip)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Trip created successfully',
            'data': trip.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error creating trip: {str(e)}'
        }), 500

@trip_bp.route('/trips/<int:trip_id>', methods=['PUT'])
def update_trip(trip_id):
    """Update an existing trip"""
    try:
        trip = Trip.query.get_or_404(trip_id)
        data = request.get_json()
        
        # Validate vehicle if provided
        if 'vehicle_id' in data:
            vehicle = Vehicle.query.get(data['vehicle_id'])
            if not vehicle:
                return jsonify({
                    'success': False,
                    'message': 'Vehicle not found'
                }), 404
        
        # Validate driver if provided
        if 'driver_id' in data:
            driver = Driver.query.get(data['driver_id'])
            if not driver:
                return jsonify({
                    'success': False,
                    'message': 'Driver not found'
                }), 404
        
        # Validate status if provided
        if 'status' in data:
            valid_statuses = ['planned', 'in_progress', 'completed', 'cancelled']
            if data['status'] not in valid_statuses:
                return jsonify({
                    'success': False,
                    'message': f'Invalid status. Must be one of: {valid_statuses}'
                }), 400
        
        # Update trip fields
        if 'vehicle_id' in data:
            trip.vehicle_id = data['vehicle_id']
        if 'driver_id' in data:
            trip.driver_id = data['driver_id']
        if 'source' in data:
            trip.source = data['source']
        if 'destination' in data:
            trip.destination = data['destination']
        if 'distance' in data:
            trip.distance = data['distance']
        if 'fuel_used' in data:
            trip.fuel_used = data['fuel_used']
        if 'trip_date' in data:
            try:
                trip.trip_date = datetime.strptime(data['trip_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Invalid trip_date format. Use YYYY-MM-DD'
                }), 400
        if 'start_time' in data:
            if data['start_time']:
                try:
                    trip.start_time = datetime.fromisoformat(data['start_time'])
                except ValueError:
                    return jsonify({
                        'success': False,
                        'message': 'Invalid start_time format. Use ISO format'
                    }), 400
            else:
                trip.start_time = None
        if 'end_time' in data:
            if data['end_time']:
                try:
                    trip.end_time = datetime.fromisoformat(data['end_time'])
                except ValueError:
                    return jsonify({
                        'success': False,
                        'message': 'Invalid end_time format. Use ISO format'
                    }), 400
            else:
                trip.end_time = None
        if 'status' in data:
            trip.status = data['status']
        if 'notes' in data:
            trip.notes = data['notes']
        
        trip.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Trip updated successfully',
            'data': trip.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating trip: {str(e)}'
        }), 500

@trip_bp.route('/trips/<int:trip_id>', methods=['DELETE'])
def delete_trip(trip_id):
    """Delete a trip"""
    try:
        trip = Trip.query.get_or_404(trip_id)
        
        db.session.delete(trip)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Trip deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error deleting trip: {str(e)}'
        }), 500

@trip_bp.route('/trips/<int:trip_id>/start', methods=['POST'])
def start_trip(trip_id):
    """Start a trip (set status to in_progress and start_time)"""
    try:
        trip = Trip.query.get_or_404(trip_id)
        
        if trip.status != 'planned':
            return jsonify({
                'success': False,
                'message': 'Trip can only be started if it is in planned status'
            }), 400
        
        trip.status = 'in_progress'
        trip.start_time = datetime.utcnow()
        trip.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Trip started successfully',
            'data': trip.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error starting trip: {str(e)}'
        }), 500

@trip_bp.route('/trips/<int:trip_id>/complete', methods=['POST'])
def complete_trip(trip_id):
    """Complete a trip (set status to completed and end_time)"""
    try:
        trip = Trip.query.get_or_404(trip_id)
        data = request.get_json() or {}
        
        if trip.status not in ['planned', 'in_progress']:
            return jsonify({
                'success': False,
                'message': 'Trip can only be completed if it is in planned or in_progress status'
            }), 400
        
        trip.status = 'completed'
        trip.end_time = datetime.utcnow()
        trip.updated_at = datetime.utcnow()
        
        # Update distance and fuel_used if provided
        if 'distance' in data:
            trip.distance = data['distance']
        if 'fuel_used' in data:
            trip.fuel_used = data['fuel_used']
        if 'notes' in data:
            trip.notes = data['notes']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Trip completed successfully',
            'data': trip.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error completing trip: {str(e)}'
        }), 500

