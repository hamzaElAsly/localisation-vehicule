import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

model = None

def train_model(df):
    global model
    X = df[['temperature', 'fuel', 'speed', 'engine_status']]
    y = df['panne']

    X_train, _, y_train, _ = train_test_split(X, y, test_size=0.2, random_state=42)
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    model = clf

def predict_failure(vehicle):
    global model
    if model is None:
        return {'error': 'Model not trained'}

    data = pd.DataFrame([{
        'temperature': vehicle.temperature,
        'fuel': vehicle.fuel,
        'speed': vehicle.speed,
        'engine_status': 1 if vehicle.engine_status else 0
    }])
    prediction = model.predict(data)[0]
    proba = model.predict_proba(data)[0][1]
    return {'prediction': int(prediction), 'probability': round(proba, 2)}

