from predict import load_model, predict, generate_alerts
from osint import enrich_alerts
from preprocess import Preprocessor
from dotenv import load_dotenv
import os
import pandas as pd

# Load environment variables
load_dotenv()

# Fetch API keys
ABUSEIPDB_API_KEY = os.getenv("ABUSEIPDB_API_KEY")
ALIENVAULT_API_KEY = os.getenv("ALIENVAULT_API_KEY")

# Load model and preprocessor
model = load_model()
preprocessor = Preprocessor()

# Load and preprocess real sample from UNSW-NB15
df = pd.read_csv("../IoT-Network-Intrusion-Detection-System-UNSW-NB15/datasets/UNSW_NB15.csv")
X, _ = preprocessor.preprocess(df)
sample = X[0:1]  # First row of real data

# Predict
predictions = predict(model, sample)
alerts = generate_alerts(predictions)

enriched_alerts = enrich_alerts(alerts, ABUSEIPDB_API_KEY, ALIENVAULT_API_KEY)

for alert in enriched_alerts:
    print("\n=== Enriched Alert ===")
    print(f"IP: {alert['src_ip']}")
    print(f"Prediction: {alert['prediction']}")
    print(f"AbuseIPDB: {alert['abuseipdb']}")
    print(f"AlienVault: {alert['alienvault']}")