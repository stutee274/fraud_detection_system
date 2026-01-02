# from xgboost import XGBClassifier
# import joblib
# import pandas as pd

# # Load preprocessed data
# X_train = pd.read_csv('processed/X_train.csv')
# y_train = pd.read_csv('processed/y_train.csv')

# xgb = XGBClassifier(
#     n_estimators=300,
#     max_depth=6,
#     learning_rate=0.1,
#     subsample=0.8,
#     colsample_bytree=0.8,
#     eval_metric='logloss'
# )
# xgb.fit(X_train, y_train)

# # Save model
# joblib.dump(xgb, "models/fraud_model_xgb.pkl")
# import joblib

# model = joblib.load("models/fraud_model_xgb.pkl")
# print("Model loaded successfully!")


# xgb.save_model("models/fraud_model_xgb.json")  # Save
# xgb2 = XGBClassifier()
# xgb2.load_model("models/fraud_model_xgb.json")  # Load
import joblib
import pandas as pd
import json
import numpy as np

# ---------- LOAD SCALER + MODEL ----------
try:
    scaler = joblib.load("model/scaler.pkl")
    model = joblib.load("models/fraud_model_xgb.pkl")
    print("Models & Scaler Loaded Successfully!")
except FileNotFoundError as e:
    print("ERROR: File not found →", e)
    print("\nMake sure you have:")
    print("fraud_detection/model/scaler.pkl")
    print("fraud_detection/model/fraud_model_xgb.pkl")
    raise SystemExit


# The order of features must match the order used for training
feature_order = ['V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7', 'V8', 'V9', 'V10', 'V11', 'V12', 'V13', 'V14', 'V15', 'V16', 'V17', 'V18', 'V19', 'V20', 'V21', 'V22', 'V23', 'V24', 'V25', 'V26', 'V27', 'V28', 'Amount', 'Hour']


# ---------- PREPROCESS NEW TRANSACTION ----------
def preprocess_transaction(data):
    """
    data = dictionary with V1..V28, Amount, Hour
    Amount is scaled using the saved scaler
    """

    df = pd.DataFrame([data])

    # Scale Amount only
    df['Amount'] = scaler.transform(df[['Amount']])

    # Reorder columns to match the training order
    return df[feature_order]


# ---------- PREDICT ----------
def predict_transaction(data):
    """
    data is a dictionary of transaction values
    """
    processed = preprocess_transaction(data)

    prediction = model.predict(processed)[0]
    proba = model.predict_proba(processed)[0][1]

    result = {
        "prediction": int(prediction),
        "probability_of_fraud": round(float(proba), 4),
        "status": "Fraud" if prediction == 1 else "Normal"
    }

    return result


# ---------- TEST RUN ----------
if __name__ == "__main__":
    test_data = {
        "Amount": 1200,
        "V1": -1.234, "V2": 0.567, "V3": -0.33, "V4": 1.22, "V5": -0.89,
        "V6": 0.12, "V7": -0.5, "V8": 0.87, "V9": -1.1, "V10": 0.04,
        "V11": -0.6, "V12": 1.5, "V13": -0.4, "V14": 0.45,
        "V15": -0.9, "V16": 0.23, "V17": -1.2, "V18": 0.56,
        "V19": -0.7, "V20": 0.32, "V21": -0.23, "V22": 0.19,
        "V23": -0.66, "V24": 0.42, "V25": -0.76, "V26": 0.05,
        "V27": -0.8, "V28": 0.9,
        "Hour": 14
    }

    result = predict_transaction(test_data)
    print("\nPrediction Result:", json.dumps(result, indent=4))

