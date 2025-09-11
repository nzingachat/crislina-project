from src.models.user import db
from datetime import datetime

class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'), nullable=False)
    source = db.Column(db.String(200), nullable=False)
    destination = db.Column(db.String(200), nullable=False)
    distance = db.Column(db.Float, nullable=True)  # in kilometers
    fuel_used = db.Column(db.Float, nullable=True)  # in liters
    trip_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    start_time = db.Column(db.DateTime, nullable=True)
    end_time = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='planned')  # planned, in_progress, completed, cancelled
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Trip {self.source} to {self.destination}>'

    def to_dict(self):
        return {
            'id': self.id,
            'vehicle_id': self.vehicle_id,
            'driver_id': self.driver_id,
            'source': self.source,
            'destination': self.destination,
            'distance': self.distance,
            'fuel_used': self.fuel_used,
            'trip_date': self.trip_date.isoformat() if self.trip_date else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'vehicle': self.vehicle.to_dict() if self.vehicle else None,
            'driver': self.driver.to_dict() if self.driver else None
        }

    def get_duration_hours(self):
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            return duration.total_seconds() / 3600
        return None

    def get_fuel_efficiency(self):
        if self.distance and self.fuel_used and self.fuel_used > 0:
            return self.distance / self.fuel_used  # km per liter
        return None

