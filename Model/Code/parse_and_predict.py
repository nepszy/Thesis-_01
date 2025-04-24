
from dotenv import load_dotenv
import os
import pandas as pd
import joblib
from predict import predict, generate_alerts
from osint import enrich_alerts

# Load environment variables
load_dotenv()
ABUSEIPDB_API_KEY = os.getenv("ABUSEIPDB_API_KEY")
ALIENVAULT_API_KEY = os.getenv("ALIENVAULT_API_KEY")

# Load model and preprocessor
model = joblib.load("knn_model.joblib")
preprocessor = joblib.load("preprocessor.joblib")

# Load real log data (.csv)
log_df = pd.read_csv("../test_log_attack.csv")

# Fix column names to match the training set
reference_df = pd.read_csv(" ")
feature_names = reference_df.columns[:-2]
log_df.columns = feature_names

# Apply same preprocessing
X_live = log_df.copy()
for col, enc in preprocessor.encoders.items():
    if col in X_live.columns:
        X_live[col] = enc.transform(X_live[col].astype(str))
X_scaled = preprocessor.scaler.transform(X_live)

# Predict and enrich
predictions = predict(model, X_scaled)
alerts = generate_alerts(predictions)
enriched_alerts = enrich_alerts(alerts, ABUSEIPDB_API_KEY, ALIENVAULT_API_KEY)

# Output
for alert in enriched_alerts:
    print("\n=== Enriched Alert ===")
    print(f"IP: {alert['src_ip']}")
    print(f"Prediction: {alert['prediction']}")
    print(f"AbuseIPDB: {alert['abuseipdb']}")
    print(f"AlienVault: {alert['alienvault']}")
