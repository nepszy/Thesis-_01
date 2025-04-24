import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder

class Preprocessor:
    def __init__(self):
        self.encoders = {}
        self.scaler = StandardScaler()

    def preprocess(self, df):
        feature_cols = df.columns[:-2]  # Exclude 'label' and 'attack_cat'
        X = df[feature_cols].copy()
        y = df['label']

        to_encode = X.select_dtypes(include=['object']).columns
        for col in to_encode:
            enc = LabelEncoder()
            X[col] = enc.fit_transform(X[col].astype(str))
            self.encoders[col] = enc

        X_scaled = self.scaler.fit_transform(X)
        return X_scaled, y