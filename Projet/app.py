from flask import Flask, render_template, request, jsonify
from datetime import datetime, timezone
from predictor import predict_failure
from predictor import train_model
import pandas as pd
import numpy as np
import threading
import random
import time
import os
from models import db, Vehicle, VehicleHistory, ActivityLog

# === Start Translation Support ===
TRANSLATIONS = {
    'en': {
        'vehicle_added': 'Vehicle Added',
        'engine_started': 'Engine Started',
        'engine_stopped': 'Engine Stopped',
        'vehicle_locked': 'Vehicle Locked',
        'vehicle_unlocked': 'Vehicle Unlocked',
        'location_request': 'Location Request',
        'emergency_stop': 'Emergency Stop',
        'vehicle_removed': 'Vehicle Removed',
        'gps_details': 'GPS coordinates: {lat}, {lng} - {address}',
        'engine_action': 'Engine {action} remotely via web interface',
        'lock_action': '{action} remotely via web interface',
        'vehicle_added_details': 'New vehicle {name} added to fleet',
        'vehicle_removed_details': 'Vehicle {name} removed from fleet',
        'emergency_details': 'Emergency stop activated - engine disabled and vehicle stopped'
    },
    'fr': {
        'vehicle_added': 'Véhicule ajouté',
        'engine_started': 'Moteur démarré',
        'engine_stopped': 'Moteur arrêté',
        'vehicle_locked': 'Véhicule verrouillé',
        'vehicle_unlocked': 'Véhicule déverrouillé',
        'location_request': 'Demande de localisation',
        'emergency_stop': 'Arrêt d urgence',
        'vehicle_removed': 'Véhicule supprimé',
        'gps_details': 'Coordonnées GPS : {lat}, {lng} - {address}',
        'engine_action': 'Moteur {action} à distance via l interface web',
        'lock_action': '{action} à distance via l interface web',
        'vehicle_added_details': 'Nouveau véhicule {name} ajouté à la flotte',
        'vehicle_removed_details': 'Véhicule {name} retiré de la flotte',
        'emergency_details': 'Arrêt d urgence activé - moteur désactivé et véhicule arrêté'
    }
}

def translate(key, lang='en', **kwargs):
    text = TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)
    return text.format(**kwargs)
# === End Translation Support   ===

app = Flask(__name__)

# Configuration DB :
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "vehicle.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'vehicle-tracking-secret-key-2024'

db.init_app(app)


# Database service class
class DatabaseService:
    @staticmethod
    def add_log(vehicle_id, action, status, details, user_id=None):
        """Add a new activity log entry"""
        try:
            log = ActivityLog(
                vehicle_id=vehicle_id,
                action=action,
                status=status,
                details=details,
                user_id=user_id
            )
            db.session.add(log)
            db.session.commit()
            return log
        except Exception as e:
            db.session.rollback()
            print(f"Error adding log: {e}")
            return None
    
    @staticmethod
    def save_vehicle_history(vehicle):
        """Save current vehicle state to history"""
        try:
            history = VehicleHistory(
                vehicle_id=vehicle.id,
                speed=vehicle.speed,
                fuel=vehicle.fuel,
                temperature=vehicle.temperature,
                latitude=vehicle.latitude,
                longitude=vehicle.longitude
            )
            db.session.add(history)
            db.session.commit()
            return history
        except Exception as e:
            db.session.rollback()
            print(f"Error saving vehicle history: {e}")
            return None
    
    @staticmethod
    def get_recent_logs(limit=20):
        """Get recent activity logs"""
        return ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(limit).all()

# Services de Vehicle
class VehicleTracker:
    def __init__(self):
        self.running = True
        
    def simulate_vehicle_updates(self):
        """Simulate real-time vehicle data updates"""
        while self.running:
            try:
                vehicles = Vehicle.query.all()
                for vehicle in vehicles:
                    if vehicle.engine_status:
                        # Simulate movement and data changes
                        old_speed = vehicle.speed
                        vehicle.speed = max(0, vehicle.speed + random.uniform(-5, 5))
                        vehicle.fuel = max(0, vehicle.fuel - random.uniform(0, 0.3))
                        vehicle.temperature = vehicle.temperature + random.uniform(-1, 2)
                        
                        # Update location slightly (simulate movement)
                        vehicle.latitude += random.uniform(-0.001, 0.001)
                        vehicle.longitude += random.uniform(-0.001, 0.001)
                        
                        # vehicle.last_update = datetime.utcnow()
                        vehicle.last_update = datetime.now(timezone.utc)
                        db.session.add(vehicle)
                        
                        # Save to history occasionally
                        if random.random() < 0.1:
                            DatabaseService.save_vehicle_history(vehicle)
                        
                        # Add random events
                        if random.random() < 0.05:  # 5% chance
                            events = [
                                ('Speed Changed', f'Speed changed from {old_speed:.1f} to {vehicle.speed:.1f} mph'),
                                ('Location Updated', f'Vehicle moved to {vehicle.latitude:.4f}, {vehicle.longitude:.4f}'),
                                ('Fuel Consumed', f'Fuel level: {vehicle.fuel:.1f}%')
                            ]
                            event_action, event_details = random.choice(events)
                            DatabaseService.add_log(vehicle.id, event_action, 'success', event_details)
                
                db.session.commit()
                time.sleep(3)  # Update every 5 seconds
                
            except Exception as e:
                print(f"Error in vehicle simulation: {e}")
                db.session.rollback()
                time.sleep(3)

# Initialisation tracker
tracker = VehicleTracker()

def init_database():
    """Initialize database with sample data"""
    with app.app_context():
        # Créer tables
        db.create_all()
        
        # Check if we already have vehicles
        if Vehicle.query.count() == 0:

            # Add sample vehicles
            vehicles_data = [
                {
                    'id': 'V1',
                    'name': 'Mercedes-Benz GLA 200 d AMG Line',
                    'latitude': 35.759465,
                    'longitude': -5.833954,
                    'address': 'Tanger, MAR',
                    'fuel': 85.5,
                    'temperature': 78.2
                },
                {
                    'id': 'V2',
                    'name': 'DACIA Sandero',
                    'latitude': 34.033333,
                    'longitude': -5.000000,
                    'address': 'Fès, MAR',
                    'fuel': 92.1,
                    'temperature': 82.5
                },
                {
                    'id': 'V3',
                    'name': 'BMW X3 xDrive20d - 197ch',
                    'latitude': 32.300815,
                    'longitude': -9.227203,
                    'address': 'Safi, MAR',
                    'fuel': 67.8,
                    'temperature': 75.9
                }
            ]
            
            for vehicle_data in vehicles_data:
                vehicle = Vehicle(**vehicle_data)
                db.session.add(vehicle)
                
                # Add initial log
                DatabaseService.add_log(
                    vehicle.id,
                    'Vehicle Added',
                    'success',
                    f'Vehicle {vehicle.name} added to tracking system'
                )
            
            db.session.commit()
            print("✅ Database initialized with sample data")


# Training de data
def generate_training_data():
    n = 1000
    df = pd.DataFrame({
        'temperature': np.random.normal(75, 10, n),
        'fuel': np.random.uniform(10, 100, n),
        'speed': np.random.uniform(0, 120, n),
        'engine_status': np.random.choice([0, 1], n),
        'panne': np.random.choice([0, 1], n, p=[0.9, 0.1])
    })
    return df

df_train = generate_training_data()
train_model(df_train)


# Routes
@app.route('/')
def dashboard():
    vehicles = Vehicle.query.all()
    recent_logs = DatabaseService.get_recent_logs(20)
    return render_template('dashboard.html',
                        vehicles=[v.to_dict() for v in vehicles],
                        logs=[log.to_dict() for log in recent_logs],
                        current_time=datetime.now()
    )

@app.route('/api/vehicles')
def get_vehicles():
    vehicles = Vehicle.query.all()
    return jsonify({v.id: v.to_dict() for v in vehicles})


@app.route('/api/logs')
def get_logs():
    logs = DatabaseService.get_recent_logs(20)
    return jsonify([log.to_dict() for log in logs])

@app.route('/api/vehicle/<vehicle_id>/engine', methods=['POST'])
def toggle_engine(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    new_status = not vehicle.engine_status
    vehicle.engine_status = new_status
    
    if new_status:
        vehicle.status = 'running'
        vehicle.speed = random.uniform(20, 60)
    else:
        vehicle.status = 'parked'
        vehicle.speed = 0
    
    vehicle.last_update = datetime.utcnow()
    db.session.commit()
    
    action = 'Engine Started' if new_status else 'Engine Stopped'
    DatabaseService.add_log(
        vehicle_id, 
        action, 
        'success', 
        f'Engine {action.lower()} remotely via web interface'
    )
    
    return jsonify({'success': True, 'engine_status': new_status})

@app.route('/api/vehicle/<vehicle_id>/lock', methods=['POST'])
def toggle_lock(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    new_status = not vehicle.lock_status
    vehicle.lock_status = new_status
    vehicle.last_update = datetime.utcnow()
    db.session.commit()
    
    action = 'Vehicle Locked' if new_status else 'Vehicle Unlocked'
    DatabaseService.add_log(
        vehicle_id,
        action,
        'success',
        f'{action} remotely via web interface'
    )
    
    return jsonify({'success': True, 'lock_status': new_status})

@app.route('/api/vehicle/<vehicle_id>/location', methods=['POST'])
def request_location(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    DatabaseService.add_log(
        vehicle_id,
        'Location Request',
        'success',
        f'GPS coordinates: {vehicle.latitude:.4f}, {vehicle.longitude:.4f} - {vehicle.address}'
    )
    
    return jsonify({
        'success': True, 
        'location': {
            'lat': vehicle.latitude,
            'lng': vehicle.longitude,
            'address': vehicle.address
        }
    })

@app.route('/api/vehicle/<vehicle_id>/emergency', methods=['POST'])
def emergency_stop(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    vehicle.engine_status = False
    vehicle.speed = 0
    vehicle.status = 'emergency_stop'
    vehicle.last_update = datetime.utcnow()
    db.session.commit()
    
    DatabaseService.add_log(
        vehicle_id,
        'Emergency Stop',
        'warning',
        'Emergency stop activated - engine disabled and vehicle stopped'
    )
    
    return jsonify({'success': True, 'status': 'emergency_stop'})

@app.route('/api/vehicle', methods=['POST'])
def add_vehicle():
    data = request.get_json()
    
    try:
        vehicle = Vehicle(
            id=data['id'],
            name=data['name'],
            latitude=data['latitude'],
            longitude=data['longitude'],
            address=data.get('address', 'Unknown Location')
        )
        db.session.add(vehicle)
        db.session.commit()
        
        DatabaseService.add_log(
            vehicle.id,
            'Vehicle Added',
            'success',
            f'New vehicle {vehicle.name} added to fleet'
        )
        
        return jsonify({'success': True, 'vehicle': vehicle.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/vehicle/<vehicle_id>', methods=['DELETE'])
def delete_vehicle(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    try:
        DatabaseService.add_log(
            vehicle_id,
            'Vehicle Removed',
            'warning',
            f'Vehicle {vehicle.name} removed from fleet'
        )
        
        db.session.delete(vehicle)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/stats')
def get_stats():
    total_vehicles = Vehicle.query.count()
    active_vehicles = Vehicle.query.filter_by(engine_status=True).count()
    total_logs = ActivityLog.query.count()
    recent_logs = ActivityLog.query.filter(
        ActivityLog.timestamp >= datetime.utcnow().replace(hour=0, minute=0, second=0)
    ).count()
    
    return jsonify({
        'total_vehicles': total_vehicles,
        'active_vehicles': active_vehicles,
        'parked_vehicles': total_vehicles - active_vehicles,
        'total_logs': total_logs,
        'today_logs': recent_logs
    })

@app.route('/api/vehicle/<vehicle_id>/predict_failure', methods=['GET'])
def predict_vehicle_failure(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)

    if not vehicle.engine_status:
        return jsonify({
            'success': False,
            'error': "Véhicule inactif. Veuillez démarrer le moteur pour activer l'analyse prédictive."
        }), 400
    
    result = predict_failure(vehicle)

    if 'error' in result:
        return jsonify({'success': False, 'error': result['error']}), 500

    return jsonify({
        'vehicle_id': vehicle.id,
        'failure_predicted': bool(result['prediction']),
        'risk_probability': result['probability']
    })



if __name__ == '__main__':
    # Initialisation DB
    init_database()
    
    # Start background thread for vehicle simulation
    data_thread = threading.Thread(target=tracker.simulate_vehicle_updates, daemon=True)
    data_thread.start()
    
    print("🚗 Vehicle Tracking System Starting...")
    print("📊 Dashboard available at: http://localhost:5000")
    print("🗄️  SQLite database: vehicle.db")
    print("📝 Persistent logging enabled")
    print("⏰ Data updates every 5 seconds")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)