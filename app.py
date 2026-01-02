# app_dual_complete.py - BANKING + CREDIT CARD Dual Mode
"""
✅ TWO MODES:
1. BANKING MODE: Raw transaction data (Transaction_Amount, Account_Balance, etc.)
2. CREDIT_CARD MODE: Pre-processed V1-V28 + Amount + Time

User selects mode via 'mode' parameter.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier
import json
import joblib
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

print("="*80)
print("🎯 DUAL MODE FRAUD DETECTION")
print("="*80)

# ============================================
# SIMPLE EXPLAINER
# ============================================
class SimpleExplainer:
    def __init__(self, model, feature_names):
        self.model = model
        self.feature_names = feature_names
        try:
            self.importances = model.feature_importances_
        except:
            self.importances = np.ones(len(feature_names)) / len(feature_names)
    
    def explain(self, X, top_n=5):
        try:
            if isinstance(X, pd.DataFrame):
                feature_values = X.iloc[0].values
            else:
                feature_values = X[0] if len(X.shape) > 1 else X
            
            contributions = feature_values * self.importances
            proba = self.model.predict_proba(X)[0][1]
            
            abs_contributions = np.abs(contributions)
            top_indices = np.argsort(abs_contributions)[-top_n:][::-1]
            
            top_features = []
            for idx in top_indices:
                contribution = float(contributions[idx])
                top_features.append({
                    "feature": self.feature_names[idx],
                    "value": round(float(feature_values[idx]), 4),
                    "shap_value": round(contribution, 4),
                    "impact": "increases" if (contribution > 0 and proba > 0.5) or (contribution < 0 and proba < 0.5) else "decreases"
                })
            
            return top_features
        except:
            return []

# ============================================
# GENAI
# ============================================
try:
    from dotenv import load_dotenv
    load_dotenv(".env")
    GENAI_ENABLED = bool(os.getenv("GROQ_API_KEY"))
    if GENAI_ENABLED:
        from genai_dual import explain_transaction
except:
    GENAI_ENABLED = False

# ============================================
# LOAD BANKING MODEL
# ============================================
model_banking = None
features_banking = None
threshold_banking = 0.4
scaler_banking = None
explainer_banking = None

try:
    if os.path.exists("models/fraud_model_banking.pkl"):
        model_banking = joblib.load("models/fraud_model_banking.pkl")
        model_type_banking = "RandomForest"
    else:
        model_banking = XGBClassifier()
        model_banking.load_model("models/fraud_model_banking.json")
        model_type_banking = "XGBoost"
    
    with open("models/features_banking.json") as f:
        features_banking = json.load(f)
    
    with open("models/model_config_banking.json") as f:
        threshold_banking = json.load(f).get("default_threshold", 0.4)
    
    scaler_banking = joblib.load("models/scaler_banking.pkl")
    explainer_banking = SimpleExplainer(model_banking, features_banking)
    
    print(f"✅ BANKING Model: {model_type_banking} ({len(features_banking)} features)")
    print(f"   Threshold: {threshold_banking}")
    
except Exception as e:
    print(f"⚠️  BANKING Model: Not available ({e})")

# ============================================
# LOAD CREDIT CARD MODEL
# ============================================
model_cc = None
features_cc = None
threshold_cc = 0.4
explainer_cc = None

try:
    # Load model
    model_cc = XGBClassifier()
    model_cc.load_model("models/fraud_model_final.json")
    
    # Load features - try different possible names
    if os.path.exists("models/feature_names.json"):
        with open("models/feature_names.json") as f:
            features_cc = json.load(f)
    elif os.path.exists("models/features.json"):
        with open("models/features.json") as f:
            features_cc = json.load(f)
    else:
        raise FileNotFoundError("features.json or feature_names.json not found")
    
    # Load config
    if os.path.exists("models/model_config.json"):
        with open("models/model_config.json") as f:
            config = json.load(f)
            threshold_cc = config.get("default_threshold", config.get("recommended_thresholds", {}).get("balanced", 0.4))
    
    explainer_cc = SimpleExplainer(model_cc, features_cc)
    
    print(f"✅ CREDIT_CARD Model: XGBoost ({len(features_cc)} features)")
    print(f"   Threshold: {threshold_cc}")
    
except Exception as e:
    print(f"⚠️  CREDIT_CARD Model: Not available ({e})")

print("="*80)
print(f"🤖 GenAI: {'✅ ENABLED' if GENAI_ENABLED else '⚠️  FALLBACK'}")
print("="*80 + "\n")

# ============================================
# BANKING MODE FEATURES
# ============================================
def prepare_banking_features(data):
    """Prepare banking features"""
    amount = float(data.get('Transaction_Amount', 0))
    balance = float(data.get('Account_Balance', 0))
    timestamp = data.get('Timestamp', '')
    txn_type = data.get('Transaction_Type', 'POS')
    daily_count = int(data.get('Daily_Transaction_Count', 1))
    avg_7d = float(data.get('Avg_Transaction_Amount_7d', amount))
    failed_count_7d = int(data.get('Failed_Transaction_Count_7d', 0))
    card_age = int(data.get('Card_Age', 100))
    txn_distance = float(data.get('Transaction_Distance', 500))
    ip_flag = int(data.get('IP_Address_Flag', 0))
    
    try:
        dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        hour, day_of_week, is_weekend = dt.hour, dt.weekday(), 1 if dt.weekday() >= 5 else 0
    except:
        hour, day_of_week, is_weekend = 12, 2, 0
    
    spend_ratio = amount / (balance + amount + 1)
    amount_vs_avg = amount / (avg_7d + 1)
    amount_log, balance_log = np.log1p(amount), np.log1p(balance)
    
    late_night = 1 if (hour >= 22 or hour <= 6) else 0
    business_hours = 1 if (9 <= hour <= 17) else 0
    early_morning = 1 if (0 <= hour <= 4) else 0
    midnight = 1 if hour == 0 else 0
    
    is_atm = 1 if 'ATM' in txn_type else 0
    is_online = 1 if 'Online' in txn_type else 0
    is_pos = 1 if 'POS' in txn_type else 0
    is_transfer = 1 if 'Transfer' in txn_type else 0
    
    high_daily_count = 1 if daily_count > 10 else 0
    low_daily_count = 1 if daily_count < 3 else 0
    moderate_daily_count = 1 if daily_count > 6 else 0
    any_failed = 1 if failed_count_7d > 0 else 0
    high_failed = 1 if failed_count_7d > 2 else 0
    
    new_card = 1 if card_age < 30 else 0
    very_new_card = 1 if card_age < 15 else 0
    old_card = 1 if card_age > 180 else 0
    
    far_transaction = 1 if txn_distance > 1000 else 0
    very_far = 1 if txn_distance > 3000 else 0
    local_transaction = 1 if txn_distance < 100 else 0
    moderate_distance = 1 if txn_distance > 500 else 0
    
    large_amount = 1 if amount > 300 else 0
    very_large = 1 if amount > 1000 else 0
    small_amount = 1 if amount < 50 else 0
    moderate_amount = 1 if amount > 150 else 0
    low_balance = 1 if balance < 5000 else 0
    very_low_balance = 1 if balance < 1000 else 0
    
    night_high_spend = 1 if (late_night and spend_ratio > 0.6) else 0
    night_large_amount = 1 if (late_night and large_amount) else 0
    distance_night = 1 if (far_transaction and late_night) else 0
    suspicious_combo = 1 if (ip_flag and late_night) else 0
    atm_night_far = 1 if (is_atm and late_night and far_transaction) else 0
    online_night = 1 if (is_online and late_night) else 0
    new_card_large = 1 if (new_card and large_amount) else 0
    weekend_night = 1 if (is_weekend and late_night) else 0
    velocity_alert = 1 if (high_daily_count and any_failed) else 0
    distance_alert = 1 if (moderate_distance and late_night) else 0
    
    features = {
        'Transaction_Amount': amount, 'Account_Balance': balance,
        'spend_ratio': spend_ratio, 'amount_vs_avg': amount_vs_avg,
        'amount_log': amount_log, 'balance_log': balance_log,
        'Hour': hour, 'DayOfWeek': day_of_week, 'Is_Weekend': is_weekend,
        'late_night': late_night, 'business_hours': business_hours,
        'early_morning': early_morning, 'midnight': midnight,
        'is_atm': is_atm, 'is_online': is_online, 'is_pos': is_pos, 'is_transfer': is_transfer,
        'Daily_Transaction_Count': daily_count, 'high_daily_count': high_daily_count,
        'low_daily_count': low_daily_count, 'moderate_daily_count': moderate_daily_count,
        'Avg_Transaction_Amount_7d': avg_7d,
        'Failed_Transaction_Count_7d': failed_count_7d, 'any_failed': any_failed,
        'high_failed': high_failed, 'high_failed_count': high_failed,
        'Card_Age': card_age, 'new_card': new_card, 'very_new_card': very_new_card, 'old_card': old_card,
        'Transaction_Distance': txn_distance, 'far_transaction': far_transaction,
        'very_far': very_far, 'local_transaction': local_transaction,
        'moderate_distance': moderate_distance, 'suspicious_ip': ip_flag,
        'large_amount': large_amount, 'very_large': very_large,
        'small_amount': small_amount, 'moderate_amount': moderate_amount,
        'low_balance': low_balance, 'very_low_balance': very_low_balance,
        'night_high_spend': night_high_spend, 'night_large_amount': night_large_amount,
        'distance_night': distance_night, 'suspicious_combo': suspicious_combo,
        'atm_night_far': atm_night_far, 'online_night': online_night,
        'new_card_large': new_card_large, 'weekend_night': weekend_night,
        'velocity_alert': velocity_alert, 'distance_alert': distance_alert
    }
    
    df = pd.DataFrame([features])
    
    # Scale
    continuous = ['Transaction_Amount', 'Account_Balance', 'spend_ratio', 'amount_vs_avg',
                  'amount_log', 'balance_log', 'Hour', 'DayOfWeek', 'Daily_Transaction_Count',
                  'Avg_Transaction_Amount_7d', 'Failed_Transaction_Count_7d',
                  'Card_Age', 'Transaction_Distance']
    
    df_scaled = df.copy()
    for col in continuous:
        if col in df_scaled.columns and scaler_banking:
            try:
                df_scaled[[col]] = scaler_banking.transform(df[[col]])
            except:
                pass
    
    # Return only features model expects
    available = [f for f in features_banking if f in df_scaled.columns]
    return df_scaled[available]

# ============================================
# CREDIT CARD MODE FEATURES
# ============================================
def prepare_credit_card_features(data):
    """Prepare credit card features (V1-V28 + Amount + Time)"""
    
    features = {}
    
    # V1-V28 (PCA features)
    for i in range(1, 29):
        v_key = f'V{i}'
        if v_key not in data:
            raise ValueError(f"Missing {v_key}. Credit card mode requires V1-V28.")
        features[v_key] = float(data[v_key])
    
    # Amount and Time
    features['Amount'] = float(data.get('Amount', 0))
    features['Time'] = float(data.get('Time', 0))
    
    # Engineered features
    hour = (features['Time'] / 3600) % 24
    features['Hour'] = hour
    features['time_gap'] = 0
    features['txn_last_1hr'] = 1
    features['Amount_log'] = np.log1p(features['Amount'])
    features['amount_roll_mean_3'] = features['Amount']
    features['amount_roll_std_3'] = 0
    
    df = pd.DataFrame([features])
    
    # Return only features model expects
    available = [f for f in features_cc if f in df.columns]
    return df[available]

# ============================================
# FALLBACK EXPLANATION
# ============================================
def generate_fallback(pred, proba, top_features, amount):
    risk = "CRITICAL" if proba >= 0.7 else "HIGH" if proba >= 0.5 else "MEDIUM" if proba >= 0.3 else "LOW"
    
    if pred == 1:
        exp = f"⚠️ FRAUD ALERT ({proba*100:.1f}% confidence)\n\n"
        exp += f"${amount:.2f} transaction flagged as {risk} RISK.\n\nKey factors:\n"
        for f in top_features[:3]:
            exp += f"• {f['feature']}: {f['value']:.2f}\n"
        exp += "\nRecommendation: Block/review."
    else:
        exp = f"✅ Normal Transaction ({(1-proba)*100:.1f}% confidence)\n\n"
        exp += f"${amount:.2f} shows {risk} risk. Recommendation: Approve."
    
    return exp

# ============================================
# API
# ============================================
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "healthy",
        "modes": {
            "banking": {
                "available": model_banking is not None,
                "features": len(features_banking) if features_banking else 0
            },
            "credit_card": {
                "available": model_cc is not None,
                "features": len(features_cc) if features_cc else 0
            }
        }
    })

@app.route("/predict", methods=["POST"])
@app.route("/api/check-fraud", methods=["POST"])
def predict():
    try:
        data = request.get_json()
        mode = data.get('mode', 'banking').lower()
        
        if mode == 'credit_card':
            # CREDIT CARD MODE
            if not model_cc:
                return jsonify({"status": "error", "message": "Credit card model unavailable"}), 400
            
            features_df = prepare_credit_card_features(data)
            proba = model_cc.predict_proba(features_df)[0][1]
            pred = int(proba >= 0.4)
            top_features = explainer_cc.explain(features_df, 5)
            amount = float(data.get('Amount', 0))
            threshold = threshold_cc
            model_name = "Credit Card (V1-V28)"
            
        else:
            # BANKING MODE (default)
            if not model_banking:
                return jsonify({"status": "error", "message": "Banking model unavailable"}), 400
            
            features_df = prepare_banking_features(data)
            proba = model_banking.predict_proba(features_df)[0][1]
            pred = int(proba >= 0.45)
            top_features = explainer_banking.explain(features_df, 5)
            amount = float(data.get('Transaction_Amount', 0))
            threshold = threshold_banking
            model_name = "Banking"
        
        # Risk
        risk = "CRITICAL" if proba >= 0.7 else "HIGH" if proba >= 0.5 else "MEDIUM" if proba >= 0.4 else "LOW" if proba >= 0.2 else "MINIMAL"
        
        # GenAI
        if GENAI_ENABLED:
            ai_exp = explain_transaction(top_features, proba, amount, mode)
        else:
            ai_exp = generate_fallback(pred, proba, top_features, amount)
        
        return jsonify({
            "status": "success",
            "mode": mode,
            "model_used": model_name,
            "prediction": pred,
            "fraud_probability": float(proba),
            "risk_level": risk,
            "threshold": threshold,
            "features_used": len(features_df.columns),
            "top_contributing_features": top_features,
            "ai_explanation": ai_exp,
            "message": "⚠️ FRAUD DETECTED" if pred == 1 else "✅ Normal",
            "transaction_amount": amount
        })
        
    except Exception as e:
        import traceback
        return jsonify({"status": "error", "message": str(e), "trace": traceback.format_exc()}), 500

if __name__ == "__main__":
    print("🚀 Dual Mode Server: http://localhost:5000")
    print("\nModes:")
    print("  • banking: Raw transaction data")
    print("  • credit_card: V1-V28 + Amount + Time\n")
    app.run(host="0.0.0.0", port=5000, debug=True)