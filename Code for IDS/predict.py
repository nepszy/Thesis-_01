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


def generate_alerts(predictions, source_data=None, ip_column=None):
    alerts = []

    # Fallback IPs for testing
    fallback_ips = [
        "45.83.64.1", "185.234.219.70", "89.248.167.131",
        "37.49.230.74", "213.186.33.5"
    ]

    for i in range(len(predictions)):
        if source_data is not None and ip_column and ip_column in source_data.columns:
            src_ip = source_data.iloc[i][ip_column]
        else:
            src_ip = fallback_ips[i % len(fallback_ips)]

        alerts.append({
            "src_ip": src_ip,
            "prediction": "Attack" if predictions[i] == 1 else "Normal"
        })

    return alerts
