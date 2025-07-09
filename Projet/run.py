import subprocess
import sys
# import os

REQUIRED_PACKAGES = [
    "flask",
    "flask_sqlalchemy",
    "scikit-learn",
    "pandas",
    "joblib"
]

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + REQUIRED_PACKAGES)
        print("✅ Packages installed successfully!")
    except subprocess.CalledProcessError:
        print("❌ Failed to install packages.")
        return False
    return True

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def main():
    print("🚗 Vehicle Tracking System - Quick Start")
    print("=" * 50)

    # Check Python version
    if not check_python_version():
        return

    # Install requirements
    if not install_requirements():
        return

    print("\n🚀 Starting Vehicle Tracking System...")
    print("📊 Dashboard will be available at: http://localhost:5000")
    print("🔧 Press Ctrl+C to stop the server")
    print("=" * 50)

    # Import and run the app
    try:

        from predictive_maintenance import train_failure_model
        from models import db, Vehicle
        from app import app, init_database, tracker
        import threading

        with app.app_context():
            # db.metadata.clear()
            db.create_all()
            # Initialize database
            init_database()
            train_failure_model()

        # Start background thread for vehicle simulation
        data_thread = threading.Thread(target=tracker.simulate_vehicle_updates, daemon=True)
        data_thread.start()

        # Run the Flask app
        app.run(debug=True, host='0.0.0.0', port=5000)

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please make sure all files are in the correct location")
    except KeyboardInterrupt:
        print("\n👋 Vehicle Tracking System stopped")
    except Exception as e:
        print(f"❌ Error starting application: {e}")

if __name__ == "__main__":
    main()
