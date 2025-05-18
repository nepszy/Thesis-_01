import json
import argparse
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix

def load_config(config_key, path="ids_train_config.json"):
    with open(path, "r") as f:
        all_configs = json.load(f)
    if config_key not in all_configs:
        raise KeyError(f"Config key '{config_key}' not found in {path}")
    return all_configs[config_key]

def train_pipeline(config_key):
    # 1) Load config & dataset
    config = load_config(config_key)
    print(f"[INFO] Loading dataset: {config['dataset']}")
    df = pd.read_csv(config["dataset"], skip_blank_lines=True, on_bad_lines="warn")

    # 2) Clean data
    df.replace([float('inf'), -float('inf')], pd.NA, inplace=True)
    df.dropna(inplace=True)
    print(f"[INFO] Cleaned training data: {df.shape[0]} rows remaining.")

    # 3) Drop unwanted columns
    df = df.drop(columns=config.get("drop_cols", []), errors="ignore")

    # 4) Encode categorical columns
    encoders = {}
    for col in config.get("categorical_cols", []):
        if col in df.columns:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            encoders[col] = le
        else:
            print(f"[WARNING] Categorical column '{col}' not found, skipping.")

    # 5) Split features and label
    y = df[config["label_col"]]
    X = df.drop(columns=[config["label_col"]], errors="ignore")

    # 6) Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 7) Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )

    # 8) Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # 9) Evaluate
    acc = model.score(X_test, y_test)
    print(f"[INFO] Model trained. Test accuracy: {acc:.4f}\n")

    # 10) Detailed metrics
    y_pred = model.predict(X_test)
    print("[INFO] Classification Report:\n")
    print(classification_report(y_test, y_pred))
    print("[INFO] Confusion Matrix:\n")
    cm = confusion_matrix(y_test, y_pred)
    print(cm, "\n")

    # 11) Save artifacts
    model_name    = f"model_{config_key}.joblib"
    scaler_name   = f"scaler_{config_key}.joblib"
    encoders_name = f"encoders_{config_key}.joblib"

    joblib.dump(model, model_name)
    joblib.dump(scaler, scaler_name)
    joblib.dump(encoders, encoders_name)
    print(f"[INFO] Artifacts saved: {model_name}, {scaler_name}, {encoders_name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Train an IDS model on a specified dataset profile."
    )
    parser.add_argument(
        "--config_key", required=True,
        help="Key in ids_train_config.json to select dataset/profile"
    )
    args = parser.parse_args()

    try:
        train_pipeline(args.config_key)
    except Exception as e:
        print(f"[ERROR] {e}")
        exit(1)
