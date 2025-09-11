from flask import Blueprint, request, jsonify
from src.models import db, Trip, Vehicle, Driver, Maintenance
from src.auth import token_required
from datetime import datetime, date, timedelta
from sqlalchemy import func, extract

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics/dashboard', methods=['GET'])
@token_required
def get_dashboard_stats(current_user):
    """Get overall dashboard statistics"""
    try:
        # Basic counts
        total_vehicles = Vehicle.query.count()
        active_vehicles = Vehicle.query.filter_by(status='active').count()
        total_drivers = Driver.query.count()
        active_drivers = Driver.query.filter_by(status='active').count()
        total_trips = Trip.query.count()
        completed_trips = Trip.query.filter_by(status='completed').count()
        
        # Recent trips (last 30 days)
        thirty_days_ago = date.today() - timedelta(days=30)
        recent_trips = Trip.query.filter(Trip.trip_date >= thirty_days_ago).count()
        
        # Total distance and fuel
        total_distance = db.session.query(func.sum(Trip.distance)).filter(Trip.distance.isnot(None)).scalar() or 0
        total_fuel = db.session.query(func.sum(Trip.fuel_used)).filter(Trip.fuel_used.isnot(None)).scalar() or 0
        
        # Maintenance costs (last 30 days)
        recent_maintenance_cost = db.session.query(func.sum(Maintenance.cost)).filter(
            Maintenance.date >= thirty_days_ago
        ).scalar() or 0
        
        stats = {
            'vehicles': {
                'total': total_vehicles,
                'active': active_vehicles,
                'maintenance': Vehicle.query.filter_by(status='maintenance').count(),
                'inactive': Vehicle.query.filter_by(status='inactive').count()
            },
            'drivers': {
                'total': total_drivers,
                'active': active_drivers,
                'inactive': Driver.query.filter_by(status='inactive').count()
            },
            'trips': {
                'total': total_trips,
                'completed': completed_trips,
                'in_progress': Trip.query.filter_by(status='in_progress').count(),
                'planned': Trip.query.filter_by(status='planned').count(),
                'recent_30_days': recent_trips
            },
            'totals': {
                'distance': round(total_distance, 2),
                'fuel_used': round(total_fuel, 2),
                'recent_maintenance_cost': round(recent_maintenance_cost, 2)
            }
        }
        
        return jsonify({
            'success': True,
            'data': stats
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching dashboard stats: {str(e)}'
        }), 500

@analytics_bp.route('/analytics/fuel-consumption', methods=['GET'])
@token_required
def get_fuel_consumption_trends(current_user):
    """Get fuel consumption trends over time"""
    try:
        days = request.args.get('days', default=30, type=int)
        start_date = date.today() - timedelta(days=days)
        
        # Query trips with fuel consumption data
        trips = Trip.query.filter(
            Trip.trip_date >= start_date,
            Trip.fuel_used.isnot(None),
            Trip.fuel_used > 0
        ).all()
        
        # Group by date
        daily_consumption = {}
        for trip in trips:
            date_str = trip.trip_date.isoformat()
            if date_str not in daily_consumption:
                daily_consumption[date_str] = 0
            daily_consumption[date_str] += trip.fuel_used
        
        # Fill missing dates with 0
        current_date = start_date
        while current_date <= date.today():
            date_str = current_date.isoformat()
            if date_str not in daily_consumption:
                daily_consumption[date_str] = 0
            current_date += timedelta(days=1)
        
        # Sort by date
        sorted_data = sorted(daily_consumption.items())
        
        return jsonify({
            'success': True,
            'data': {
                'labels': [item[0] for item in sorted_data],
                'values': [round(item[1], 2) for item in sorted_data]
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching fuel consumption trends: {str(e)}'
        }), 500

@analytics_bp.route('/analytics/trips-per-vehicle', methods=['GET'])
@token_required
def get_trips_per_vehicle(current_user):
    """Get number of trips per vehicle"""
    try:
        # Query trips grouped by vehicle
        results = db.session.query(
            Vehicle.reg_no,
            Vehicle.model,
            func.count(Trip.id).label('trip_count')
        ).outerjoin(Trip).group_by(Vehicle.id).all()
        
        vehicles = []
        trip_counts = []
        
        for reg_no, model, count in results:
            vehicles.append(f"{reg_no} ({model})")
            trip_counts.append(count)
        
        return jsonify({
            'success': True,
            'data': {
                'labels': vehicles,
                'values': trip_counts
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching trips per vehicle: {str(e)}'
        }), 500

@analytics_bp.route('/analytics/trips-per-driver', methods=['GET'])
@token_required
def get_trips_per_driver(current_user):
    """Get number of trips per driver"""
    try:
        # Query trips grouped by driver
        results = db.session.query(
            Driver.name,
            func.count(Trip.id).label('trip_count')
        ).outerjoin(Trip).group_by(Driver.id).all()
        
        drivers = []
        trip_counts = []
        
        for name, count in results:
            drivers.append(name)
            trip_counts.append(count)
        
        return jsonify({
            'success': True,
            'data': {
                'labels': drivers,
                'values': trip_counts
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching trips per driver: {str(e)}'
        }), 500

@analytics_bp.route('/analytics/maintenance-costs', methods=['GET'])
@token_required
def get_maintenance_cost_trends(current_user):
    """Get maintenance cost trends over time"""
    try:
        months = request.args.get('months', default=12, type=int)
        start_date = date.today() - timedelta(days=months * 30)
        
        # Query maintenance records
        records = Maintenance.query.filter(Maintenance.date >= start_date).all()
        
        # Group by month
        monthly_costs = {}
        for record in records:
            month_key = record.date.strftime('%Y-%m')
            if month_key not in monthly_costs:
                monthly_costs[month_key] = 0
            monthly_costs[month_key] += record.cost
        
        # Fill missing months with 0
        current_date = start_date.replace(day=1)
        while current_date <= date.today():
            month_key = current_date.strftime('%Y-%m')
            if month_key not in monthly_costs:
                monthly_costs[month_key] = 0
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        # Sort by month
        sorted_data = sorted(monthly_costs.items())
        
        return jsonify({
            'success': True,
            'data': {
                'labels': [item[0] for item in sorted_data],
                'values': [round(item[1], 2) for item in sorted_data]
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching maintenance cost trends: {str(e)}'
        }), 500

@analytics_bp.route('/analytics/vehicle-utilization', methods=['GET'])
@token_required
def get_vehicle_utilization(current_user):
    """Get vehicle utilization rates"""
    try:
        days = request.args.get('days', default=30, type=int)
        start_date = date.today() - timedelta(days=days)
        
        vehicles = Vehicle.query.all()
        utilization_data = []
        
        for vehicle in vehicles:
            # Count unique days with trips
            trip_dates = db.session.query(func.distinct(Trip.trip_date)).filter(
                Trip.vehicle_id == vehicle.id,
                Trip.trip_date >= start_date
            ).count()
            
            utilization_rate = (trip_dates / days) * 100 if days > 0 else 0
            
            utilization_data.append({
                'vehicle': f"{vehicle.reg_no} ({vehicle.model})",
                'utilization_rate': round(utilization_rate, 1),
                'days_used': trip_dates,
                'total_days': days
            })
        
        # Sort by utilization rate
        utilization_data.sort(key=lambda x: x['utilization_rate'], reverse=True)
        
        return jsonify({
            'success': True,
            'data': utilization_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching vehicle utilization: {str(e)}'
        }), 500

@analytics_bp.route('/analytics/fuel-efficiency', methods=['GET'])
@token_required
def get_fuel_efficiency(current_user):
    """Get fuel efficiency data for vehicles"""
    try:
        # Query trips with both distance and fuel data
        results = db.session.query(
            Vehicle.reg_no,
            Vehicle.model,
            Vehicle.fuel_type,
            func.sum(Trip.distance).label('total_distance'),
            func.sum(Trip.fuel_used).label('total_fuel')
        ).join(Trip).filter(
            Trip.distance.isnot(None),
            Trip.fuel_used.isnot(None),
            Trip.distance > 0,
            Trip.fuel_used > 0
        ).group_by(Vehicle.id).all()
        
        efficiency_data = []
        for reg_no, model, fuel_type, total_distance, total_fuel in results:
            if total_fuel > 0:
                efficiency = total_distance / total_fuel  # km per liter
                efficiency_data.append({
                    'vehicle': f"{reg_no} ({model})",
                    'fuel_type': fuel_type,
                    'efficiency': round(efficiency, 2),
                    'total_distance': round(total_distance, 2),
                    'total_fuel': round(total_fuel, 2)
                })
        
        # Sort by efficiency
        efficiency_data.sort(key=lambda x: x['efficiency'], reverse=True)
        
        return jsonify({
            'success': True,
            'data': efficiency_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching fuel efficiency: {str(e)}'
        }), 500

