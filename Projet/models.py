from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Vehicle(db.Model):
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'vehicles'
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    speed = db.Column(db.Float, default=0.0)
    fuel = db.Column(db.Float, default=100.0)
    temperature = db.Column(db.Float, default=75.0)
    engine_status = db.Column(db.Boolean, default=False)
    lock_status = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(50), default='parked')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_update = db.Column(db.DateTime, default=datetime.utcnow)

    # Relations avec logs
    logs = db.relationship('ActivityLog', backref='vehicle', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'location': {
                'lat': self.latitude,
                'lng': self.longitude,
                'address': self.address
            },
            'speed': self.speed,
            'fuel': self.fuel,
            'temperature': self.temperature,
            'engine_status': self.engine_status,
            'lock_status': self.lock_status,
            'status': self.status,
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.String(50), db.ForeignKey('vehicles.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    action = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    details = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.String(50), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'vehicle_id': self.vehicle_id,
            'timestamp': self.timestamp.isoformat(),
            'action': self.action,
            'status': self.status,
            'details': self.details,
            'user_id': self.user_id
        }

class VehicleHistory(db.Model):
    __tablename__ = 'vehicle_history'
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.String(50), db.ForeignKey('vehicles.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    speed = db.Column(db.Float, nullable=False)
    fuel = db.Column(db.Float, nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
