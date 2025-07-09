# predictive_maintenance.py
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
from models import db, VehicleHistory

MODEL_PATH = 'model/failure_predictor.pkl'

def train_failure_model():
    """Entraîne un modèle de prédiction de pannes à partir des données VehicleHistory"""
    history = VehicleHistory.query.all()

    if not history:
        print("❌ Aucune donnée disponible dans VehicleHistory.")
        return

    # Préparer les données
    data = pd.DataFrame([{
        'temperature': h.temperature,
        'fuel': h.fuel,
        'speed': h.speed,
        'vehicle_id': h.vehicle_id
    } for h in history])

    # Simuler des étiquettes de pannes : température élevée OU carburant bas
    data['panne'] = ((data['temperature'] > 90) | (data['fuel'] < 10)).astype(int)

    # Features et cible
    X = data[['temperature', 'fuel', 'speed']]
    y = data['panne']

    # Split pour test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Entraînement
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Évaluation
    print("📊 Résultats du modèle :")
    print(classification_report(y_test, model.predict(X_test)))

    # Sauvegarde
    joblib.dump(model, MODEL_PATH)
    print(f"✅ Modèle enregistré : {MODEL_PATH}")

def load_failure_model():
    """Charge le modèle de prédiction si disponible"""
    try:
        return joblib.load(MODEL_PATH)
    except Exception as e:
        print(f"⚠️ Erreur de chargement du modèle : {e}")
        return None
    