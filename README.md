# AI-Powered Intrusion Detection System (IDS) Project
## Overview
This project builds a dynamic AI-based Intrusion Detection System (IDS) by Python.
It allows you to:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
- Train models on multiple network traffic datasets (like CICIDS2018, UNSW-NB15, etc.)  -
- Predict attacks dynamically                                                           -
- Enrich detected alerts with OSINT data (AbuseIPDB, AlienVault)                        -
- Fully automate training and prediction with a master script                           -
- Save and organize results neatly                                                      -
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Project Structure
```
/AI
  /CSE-CIC-IDS2018 (dataset folder
  /Dataset_UNSW_NB15
  /Code
    /Prototype_Code
    main.py
    master.py
    osint.py
    predict.py
    preprocess.py
    train_all.py
    training.py
    ids_train_config.json
    /results (generated after running)
    
```
---

## How to Use

### 1. Prepare Datasets
Place your CSV datasets into the project folder.

### 2. Prepare Configuration
Edit or create `ids_train_config.json` with:
- Dataset paths
- Label column name
- Categorical columns
- Columns to drop

Example:
```json
{
  "friday_16_02_2018": {
    "dataset": "Friday-16-02-2018_TrafficForML_CICFlowMeter.csv",
    "label_col": "Label",
    "categorical_cols": ["Protocol"],
    "drop_cols": ["Timestamp", "Dst Port", "Src IP", "Dst IP", "Src Port", "Flow ID"]
  }
}
```

### 3. Train Models
```bash
python3 training.py --config_key friday_16_02_2018
```
Or train all:
```bash
python3 train_all.py
```

### 4. Predict Attacks
```bash
python3 main.py --file Friday-16-02-2018_TrafficForML_CICFlowMeter.csv --config_key friday_16_02_2018
```

### 5. Full Automation
To train and predict all datasets at once:
```bash
python3 master.py
```

---

## Outputs
- Trained models: `model_{config_key}.joblib`
- Scalers and encoders
- Alerts CSVs: `/results/alerts_{config_key}.csv`
- Summary log: `summary_log.txt`

---

## Features
- Dynamic dataset handling
- OSINT IP reputation enrichment
- Skips missing fields automatically
- No crashes on messy CSVs
- Professional automation ready for research and production

---

## Requirements
- Python 3.8+
- pandas
- scikit-learn
- python-dotenv
- joblib

Install packages:
```bash
pip3 install numpy pandas tensorflow scikit-learn
```

---

## Notes
- Make sure API keys for AbuseIPDB and AlienVault are stored in `.env` file
- If your datasets have inconsistent columns, update the config accordingly
- This system focuses on supervised learning; unsupervised extensions can be added later

---

## Author
- Group 28 from CDU 

