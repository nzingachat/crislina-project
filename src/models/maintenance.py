from src.models.user import db
from datetime import datetime

class Maintenance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    cost = db.Column(db.Float, nullable=False, default=0.0)
    description = db.Column(db.Text, nullable=False)
    maintenance_type = db.Column(db.String(50), nullable=False)  # routine, repair, emergency
    service_provider = db.Column(db.String(200), nullable=True)
    mileage = db.Column(db.Integer, nullable=True)  # vehicle mileage at time of maintenance
    next_service_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='completed')  # scheduled, in_progress, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Maintenance {self.vehicle.reg_no if self.vehicle else "Unknown"} - {self.maintenance_type}>'

    def to_dict(self):
        return {
            'id': self.id,
            'vehicle_id': self.vehicle_id,
            'date': self.date.isoformat() if self.date else None,
            'cost': self.cost,
            'description': self.description,
            'maintenance_type': self.maintenance_type,
            'service_provider': self.service_provider,
            'mileage': self.mileage,
            'next_service_date': self.next_service_date.isoformat() if self.next_service_date else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'vehicle': self.vehicle.to_dict() if self.vehicle else None
        }

