import argparse
import pandas as pd
import joblib
import json
import os
from dotenv import load_dotenv
from predict import predict, generate_alerts
from osint import enrich_alerts
from preprocess import Preprocessor

# Load .env
load_dotenv()
ABUSEIPDB_API_KEY = os.getenv("ABUSEIPDB_API_KEY")
ALIENVAULT_API_KEY = os.getenv("ALIENVAULT_API_KEY")

def load_config():
    with open("ids_train_config.json", "r") as f:
        return json.load(f)

def load_model_and_preprocessor(config_key):
    model = joblib.load(f"model_{config_key}.joblib")
    scaler = joblib.load(f"scaler_{config_key}.joblib")
    encoders = joblib.load(f"encoders_{config_key}.joblib")
    
    preprocessor = Preprocessor()
    preprocessor.scaler = scaler
    preprocessor.encoders = encoders
    return model, preprocessor


def process_log_file(model, preprocessor, path, config):
    print(f"[INFO] Processing log file: {path}")
    df = pd.read_csv(path, skip_blank_lines=True, on_bad_lines='warn')

    # Clean dataset
    df.replace([float('inf'), -float('inf')], pd.NA, inplace=True)
    df.dropna(inplace=True)
    print(f"[INFO] Cleaned data: {df.shape[0]} rows remaining after dropna.")

    # Drop unwanted columns
    df = df.drop(columns=config.get("drop_cols", []), errors="ignore")
    if config.get("label_col"):
        df = df.drop(columns=[config["label_col"]], errors="ignore")


    # Encode categoricals
    for col, enc in preprocessor.encoders.items():
        if col in df.columns:
            df[col] = enc.transform(df[col].astype(str))
        else:
            print(f"[WARNING] Categorical column '{col}' missing during prediction, skipping...")


    # Align test features with training columns
    train_df = pd.read_csv(config["dataset"])
    train_df = train_df.drop(columns=config.get("drop_cols", []), errors="ignore")
    if config.get("label_col"):
        X_columns = train_df.drop(columns=[config["label_col"]], errors="ignore").columns
    else:
        X_columns = train_df.columns

    df = df[X_columns]

    # Scale
    X_scaled = preprocessor.scaler.transform(df)

    # Predict
    predictions = predict(model, X_scaled)
    print(f"[INFO] Total predictions: {len(predictions)}")
    print(f"[INFO] Attack predictions: {sum(1 for p in predictions if p == 1)}")

    # Auto-detect IP column
    possible_ip_columns = ["src_ip", "Src IP", "Source IP", "SrcIP", "source_ip"]
    ip_column_found = next((col for col in possible_ip_columns if col in df.columns), None)
    print(f"[INFO] Detected IP column: {ip_column_found}")

    alerts = generate_alerts(predictions, source_data=df, ip_column=ip_column_found)
    if alerts:
        print("[DEBUG] First alert:", alerts[0])
    attack_alerts = [a for a in alerts if a["prediction"] == "Attack"]
    enriched_alerts = enrich_alerts(attack_alerts, ABUSEIPDB_API_KEY, ALIENVAULT_API_KEY)

    for alert in enriched_alerts:
        print("\n=== Enriched Alert ===")
        print(f"IP: {alert['src_ip']}")
        print(f"Prediction: {alert['prediction']}")
        print(f"AbuseIPDB: {alert['abuseipdb']}")
        print(f"AlienVault: {alert['alienvault']}")

    # Save alerts to CSV
    import csv
    output_path = "alerts_output.csv"
    with open(output_path, "w", newline="") as csvfile:
        fieldnames = ["src_ip", "prediction", "abuse_confidence", "total_reports", "country", "reputation", "pulses"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for alert in enriched_alerts:
            writer.writerow({
                "src_ip": alert["src_ip"],
                "prediction": alert["prediction"],
                "abuse_confidence": alert["abuseipdb"].get("abuseConfidenceScore", "N/A"),
                "total_reports": alert["abuseipdb"].get("totalReports", "N/A"),
                "country": alert["abuseipdb"].get("countryCode", "N/A"),
                "reputation": alert["alienvault"].get("reputation", "N/A"),
                "pulses": alert["alienvault"].get("pulse_info", "N/A")
            })

    print(f"\n✅ Alerts saved to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, help="Path to log file for batch prediction")
    parser.add_argument("--config_key", required=True, help="Configuration profile name from the config file")
    args = parser.parse_args()

    all_configs = load_config()
    config = all_configs[args.config_key]
    model, preprocessor = load_model_and_preprocessor(args.config_key)
    process_log_file(model, preprocessor, args.file, config)
