import os
import json

# Load all configs
with open("ids_train_config.json", "r") as f:
    all_configs = json.load(f)

# Loop through all keys
for config_key in all_configs.keys():
    print(f"\n🚀 Training model for config: {config_key}")
    os.system(f"python3 training.py --config_key {config_key}")

print("\n✅ Finished training all models!")
