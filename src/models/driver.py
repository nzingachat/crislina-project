from src.models.user import db
from datetime import datetime

class Driver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    license_no = db.Column(db.String(50), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='active')  # active, inactive
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign key to link with User (optional - if driver has a user account)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Relationships
    trips = db.relationship('Trip', backref='driver', lazy=True)

    def __repr__(self):
        return f'<Driver {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'license_no': self.license_no,
            'phone': self.phone,
            'email': self.email,
            'status': self.status,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def get_total_trips(self):
        return len(self.trips)

    def get_total_distance(self):
        return sum(trip.distance for trip in self.trips if trip.distance)

    def get_total_fuel_used(self):
        return sum(trip.fuel_used for trip in self.trips if trip.fuel_used)

