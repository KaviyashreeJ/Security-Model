import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import joblib

def train_model():
    # Load dataset
    df = pd.read_csv("C:/Cloud Storage and Security/Security Model/Security-Model/data.csv")
    
    # Assuming 'features' is a list of columns used for training
    features = df.columns[:-1]  # All except the last column
    X = df[features]

    # Train Isolation Forest
    model = IsolationForest(n_estimators=100, contamination=0.1, random_state=42)
    model.fit(X)

    # Save model
    joblib.dump(model, "model.pkl")
    print("Model trained and saved.")

if __name__ == "__main__":
    train_model()
