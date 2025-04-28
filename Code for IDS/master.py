import os
import json
import argparse

def load_all_configs(config_file):
    with open(config_file, "r") as f:
        return json.load(f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config_file", default="ids_train_config.json", help="Path to config JSON file")
    args = parser.parse_args()

    all_configs = load_all_configs(args.config_file)

    # Create results folder if not exists
    if not os.path.exists("results"):
        os.makedirs("results")

    # Clean old summary log
    open("summary_log.txt", "w").close()

    # Phase 1: Train all configs
    for config_key in all_configs.keys():
        print(f"\n🚀 Training model for config: {config_key}")
        os.system(f"python3 training.py --config_key {config_key} --config_file {args.config_file}")

    # Phase 2: Predict all configs
    for config_key, config in all_configs.items():
        print(f"\n🔍 Predicting alerts for config: {config_key}")
        dataset_path = config["dataset"]

        # Predict and move alerts
        predict_command = f"python3 main.py --file \"{dataset_path}\" --config_key {config_key}"
        os.system(predict_command)

        alert_file = f"alerts_{config_key}.csv"
        if os.path.exists(alert_file):
            os.rename(alert_file, f"results/{alert_file}")

    print("\n✅ Master run completed for all configs!")
