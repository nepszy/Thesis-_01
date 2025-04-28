import json
import argparse
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier

def load_config(config_key, path="ids_train_config.json"):
    with open(path, "r") as f:
        all_configs = json.load(f)
    return all_configs[config_key]

def train_pipeline(config, config_key):
    print(f"[INFO] Loading dataset: {config['dataset']}")
    df = pd.read_csv(config["dataset"], skip_blank_lines=True, on_bad_lines='warn')

    # Drop unwanted columns
    df = df.drop(columns=config.get("drop_cols", []), errors="ignore")
    
    # Remove any rows with non-numeric values
    df = df[pd.to_numeric(df.select_dtypes(include=[object]).stack(), errors='coerce').unstack().isna().all(axis=1)]

    # Clean dataset
    df.replace([float('inf'), -float('inf')], pd.NA, inplace=True)
    df.dropna(inplace=True)
    print(f"[INFO] Cleaned training data: {df.shape[0]} rows remaining.")

    # Encode categorical columns
    encoders = {}
    for col in config.get("categorical_cols", []):
        if col in df.columns:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            encoders[col] = le
        else:
            print(f"[WARNING] Categorical column '{col}' not found, skipping...")

    # Separate features and label
    if config.get("label_col"):
        y = df[config["label_col"]]
        X = df.drop(columns=[config["label_col"]])
    else:
        print("[WARNING] No label_col provided. Using entire dataset for X only.")
        X = df
        y = None
        
    # Ensure X is only numeric (drop any non-numeric columns)
    X = X.select_dtypes(include=["number"])

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Check if enough samples
    if X_scaled.shape[0] < 5:
        raise ValueError(f"❌ Not enough samples ({X_scaled.shape[0]}) to split train/test for {config_key}. Check your dataset or clean your config.")

    # Train/test split (only if labels exist)
    if y is not None:
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )

        # Train model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        # Evaluate
        acc = model.score(X_test, y_test)
        print(f"[INFO] Model trained. Test accuracy: {acc:.4f}")
    else:
        # No label, unsupervised training not implemented yet
        raise ValueError("Label column missing. Cannot train supervised model.")

    # Save artifacts
    model_name = f"model_{config_key}.joblib"
    scaler_name = f"scaler_{config_key}.joblib"
    encoders_name = f"encoders_{config_key}.joblib"

    joblib.dump(model, model_name)
    joblib.dump(scaler, scaler_name)
    joblib.dump(encoders, encoders_name)

    print(f"[INFO] Artifacts saved as: {model_name}, {scaler_name}, {encoders_name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config_key", required=True, help="Configuration key to use")
    parser.add_argument("--config_file", default="ids_train_config.json", help="Path to configuration JSON file")
    args = parser.parse_args()


    config = load_config(args.config_key, args.config_file)
    train_pipeline(config, args.config_key)
