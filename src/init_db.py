#!/usr/bin/env python3
"""
Database initialization script for Vehicle Fleet Management System
Creates sample data for testing and development
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime, date, timedelta
from src.models import db, User, Vehicle, Driver, Trip, Maintenance
from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
    db.init_app(app)
    return app

def init_database():
    app = create_app()
    
    with app.app_context():
        # Drop all tables and recreate
        db.drop_all()
        db.create_all()
        
        # Create admin user
        admin = User(
            username='admin',
            email='admin@fleetmanagement.com',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Create manager user
        manager = User(
            username='manager',
            email='manager@fleetmanagement.com',
            role='manager'
        )
        manager.set_password('manager123')
        db.session.add(manager)
        
        # Create driver user
        driver_user = User(
            username='driver1',
            email='driver1@fleetmanagement.com',
            role='driver'
        )
        driver_user.set_password('driver123')
        db.session.add(driver_user)
        
        # Create sample vehicles
        vehicles = [
            Vehicle(reg_no='ABC-123', model='Toyota Camry', fuel_type='petrol', status='active'),
            Vehicle(reg_no='XYZ-456', model='Ford Transit', fuel_type='diesel', status='active'),
            Vehicle(reg_no='DEF-789', model='Tesla Model 3', fuel_type='electric', status='active'),
            Vehicle(reg_no='GHI-012', model='Honda Civic', fuel_type='petrol', status='maintenance'),
            Vehicle(reg_no='JKL-345', model='Nissan Leaf', fuel_type='electric', status='active')
        ]
        
        for vehicle in vehicles:
            db.session.add(vehicle)
        
        # Create sample drivers
        drivers = [
            Driver(name='John Smith', license_no='DL001', phone='+1234567890', email='john@example.com', user_id=3),
            Driver(name='Sarah Johnson', license_no='DL002', phone='+1234567891', email='sarah@example.com'),
            Driver(name='Mike Wilson', license_no='DL003', phone='+1234567892', email='mike@example.com'),
            Driver(name='Emily Davis', license_no='DL004', phone='+1234567893', email='emily@example.com')
        ]
        
        for driver in drivers:
            db.session.add(driver)
        
        # Commit to get IDs
        db.session.commit()
        
        # Create sample trips
        base_date = date.today() - timedelta(days=30)
        trips = [
            Trip(vehicle_id=1, driver_id=1, source='New York', destination='Boston', 
                 distance=215.0, fuel_used=18.5, trip_date=base_date, status='completed'),
            Trip(vehicle_id=2, driver_id=2, source='Chicago', destination='Detroit', 
                 distance=280.0, fuel_used=25.0, trip_date=base_date + timedelta(days=1), status='completed'),
            Trip(vehicle_id=3, driver_id=3, source='Los Angeles', destination='San Francisco', 
                 distance=380.0, fuel_used=0.0, trip_date=base_date + timedelta(days=2), status='completed'),
            Trip(vehicle_id=1, driver_id=1, source='Boston', destination='Philadelphia', 
                 distance=300.0, fuel_used=24.0, trip_date=base_date + timedelta(days=3), status='completed'),
            Trip(vehicle_id=5, driver_id=4, source='Miami', destination='Orlando', 
                 distance=235.0, fuel_used=0.0, trip_date=base_date + timedelta(days=4), status='completed'),
            Trip(vehicle_id=2, driver_id=2, source='Houston', destination='Dallas', 
                 distance=240.0, fuel_used=22.0, trip_date=base_date + timedelta(days=5), status='in_progress'),
            Trip(vehicle_id=1, driver_id=1, source='Seattle', destination='Portland', 
                 distance=173.0, fuel_used=15.0, trip_date=date.today(), status='planned')
        ]
        
        for trip in trips:
            db.session.add(trip)
        
        # Create sample maintenance records
        maintenance_records = [
            Maintenance(vehicle_id=1, date=base_date - timedelta(days=10), cost=150.0, 
                       description='Oil change and filter replacement', maintenance_type='routine'),
            Maintenance(vehicle_id=2, date=base_date - timedelta(days=5), cost=450.0, 
                       description='Brake pad replacement', maintenance_type='repair'),
            Maintenance(vehicle_id=4, date=base_date, cost=1200.0, 
                       description='Engine repair', maintenance_type='emergency', status='in_progress'),
            Maintenance(vehicle_id=3, date=base_date - timedelta(days=15), cost=80.0, 
                       description='Tire rotation and inspection', maintenance_type='routine'),
            Maintenance(vehicle_id=5, date=base_date - timedelta(days=20), cost=200.0, 
                       description='Battery replacement', maintenance_type='repair')
        ]
        
        for maintenance in maintenance_records:
            db.session.add(maintenance)
        
        # Commit all changes
        db.session.commit()
        
        print("Database initialized successfully!")
        print("\nDefault users created:")
        print("Admin: username='admin', password='admin123'")
        print("Manager: username='manager', password='manager123'")
        print("Driver: username='driver1', password='driver123'")
        print(f"\nSample data created:")
        print(f"- {len(vehicles)} vehicles")
        print(f"- {len(drivers)} drivers")
        print(f"- {len(trips)} trips")
        print(f"- {len(maintenance_records)} maintenance records")

if __name__ == '__main__':
    init_database()

