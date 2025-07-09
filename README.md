# 🚗 Système de Suivi & Contrôle de Véhicule à Distance

Ce projet propose une **application web intelligente** permettant de **suivre en temps réel**, **contrôler à distance**, et **prédire les pannes potentielles** d’un véhicule connecté.  
Le système combine des outils Python modernes avec une simulation de capteurs pour offrir une expérience télématique complète.

---

## ✅ Fonctionnalités principales

- 🔐 **Verrouillage / Déverrouillage du véhicule**
- 🚀 **Démarrage & arrêt du moteur à distance**
- 📍 **Visualisation de la position GPS sur carte (Folium)**
- 📊 **Consultation des logs d'activité**
- 🧠 **Prédiction de panne par Intelligence Artificielle (Random Forest)**
- 🚨 **Réaction en cas d’urgence (arrêt immédiat + localisation)**
- 🌡️ **Surveillance de la vitesse, température et carburant en temps réel**
- 🌐 **Interface Web intuitive (Flask + Jinja2)**

---

## 🧱 Aperçu de l’architecture & Installation 

```plaintext
               ┌────────────────────────────┐
               │ Interface Web (HTML/JS)    │
               └────────────┬───────────────┘
                            │
                      HTTP Requests
                            │
                     ┌──────▼──────┐
                     │  Flask API  │
                     └──────┬──────┘
                            │
         ┌──────────────────┼───────────────────┐
         │                  │                   │
┌────────▼─────┐   ┌────────▼──────┐    ┌───────▼────────┐
│ SQLite DB    │   │ Simulateur    │    │ IA prédictive  │
│ (Vehicles +  │   │ de capteurs   │    │ (predictor.py) │
│ Logs/History)│   │ (threading)   │    │ RandomForest   │
└──────────────┘   └───────────────┘    └────────────────┘



# Installer les bibliothèques nécessaires :
pip install -r requirements.txt

# Cloner le projet :
git clone https://github.com/votre-repo/vehicle-tracking.git
cd vehicle-tracking

# Execution de Projet :
python run.py
```
