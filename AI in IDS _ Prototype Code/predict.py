import joblib
import numpy as np

def load_model():
    model = joblib.load("knn_model.joblib")
    return model

def load_preprocessor():
    preprocessor = joblib.load("preprocessor.joblib")
    return preprocessor

def predict(model, X):
    return model.predict(X)

def generate_alerts(predictions):
    alerts = []
    for i in range(len(predictions)):
        alerts.append({
            "src_ip": f"192.168.1.{i+1}",
            "prediction": "Attack" if predictions[i] == 1 else "Normal"
        })
    return alerts