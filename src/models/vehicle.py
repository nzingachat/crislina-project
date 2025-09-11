from src.models.user import db
from datetime import datetime

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reg_no = db.Column(db.String(20), unique=True, nullable=False)
    model = db.Column(db.String(100), nullable=False)
    fuel_type = db.Column(db.String(20), nullable=False)  # petrol, diesel, electric
    status = db.Column(db.String(20), nullable=False, default='active')  # active, maintenance, inactive
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    trips = db.relationship('Trip', backref='vehicle', lazy=True)
    maintenance_records = db.relationship('Maintenance', backref='vehicle', lazy=True)

    def __repr__(self):
        return f'<Vehicle {self.reg_no}>'

    def to_dict(self):
        return {
            'id': self.id,
            'reg_no': self.reg_no,
            'model': self.model,
            'fuel_type': self.fuel_type,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def get_total_trips(self):
        return len(self.trips)

    def get_total_distance(self):
        return sum(trip.distance for trip in self.trips if trip.distance)

    def get_total_fuel_used(self):
        return sum(trip.fuel_used for trip in self.trips if trip.fuel_used)

