# app_match_model.py - Matches YOUR saved model features!
"""
This app creates the EXACT 43 features your model was trained on:
- midnight, is_transfer, low_daily_count, very_new_card
- local_transaction, very_large, small_amount, very_low_balance
- suspicious_combo, atm_night_far, online_night
- new_card_large, weekend_night
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier
import json
import joblib
import shap
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

print("="*80)
print("🎯 BANKING FRAUD DETECTION - MATCHED TO YOUR MODEL")
print("="*80)

# ============================================
# LOAD BANKING MODEL
# ============================================
print("\n📦 Loading Banking Model...")

model_bank = None
features_bank = None
threshold_bank = 0.4
scaler_bank = None

try:
    # Try loading Random Forest first
    if os.path.exists("models/fraud_model_banking.pkl"):
        model_bank = joblib.load("models/fraud_model_banking.pkl")
        model_type = "Random Forest"
    else:
        # Fall back to XGBoost
        model_bank = XGBClassifier()
        model_bank.load_model("models/fraud_model_banking.json")
        model_type = "XGBoost"
    
    # Load features
    with open("models/features_banking.json") as f:
        features_bank = json.load(f)
    
    # Load config
    with open("models/model_config_banking.json") as f:
        config_bank = json.load(f)
        threshold_bank = config_bank.get("default_threshold", 0.4)
    
    # Load scaler
    scaler_bank = joblib.load("models/scaler_banking.pkl")
    
    print(f"   Banking Model loaded ({model_type})")
    print(f"      • Features: {len(features_bank)}")
    print(f"      • Threshold: {threshold_bank}")
    print(f"\n    Expected features:")
    for i, feat in enumerate(features_bank, 1):
        print(f"      {i:2}. {feat}")
    
except Exception as e:
    print(f"    Banking Model ERROR: {e}")
    exit(1)

print("="*80 + "\n")

# ============================================
# PREPARE FEATURES - EXACT MATCH TO MODEL
# ============================================

def prepare_features_bank(data):
    """Prepare features matching EXACTLY what model was trained on"""
    
    # Extract inputs
    amount = float(data.get('Transaction_Amount', 0))
    balance = float(data.get('Account_Balance', 0))
    timestamp = data.get('Timestamp', '')
    txn_type = data.get('Transaction_Type', 'POS')
    daily_count = int(data.get('Daily_Transaction_Count', 1))
    avg_7d = float(data.get('Avg_Transaction_Amount_7d', amount))
    card_age = int(data.get('Card_Age', 100))
    txn_distance = float(data.get('Transaction_Distance', 500))
    ip_flag = int(data.get('IP_Address_Flag', 0))
    
    # Parse timestamp
    try:
        dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        hour = dt.hour
        day_of_week = dt.weekday()
        is_weekend = 1 if day_of_week >= 5 else 0
    except:
        hour = 12
        day_of_week = 2
        is_weekend = 0
    
    # Calculate derived features
    spend_ratio = amount / (balance + amount + 1)
    amount_vs_avg = amount / (avg_7d + 1)
    
    # Time features
    late_night = 1 if (hour >= 22 or hour <= 6) else 0
    business_hours = 1 if (9 <= hour <= 17) else 0
    early_morning = 1 if (0 <= hour <= 4) else 0
    midnight = 1 if hour == 0 else 0  # NEW!
    
    # Transaction types
    is_atm = 1 if 'ATM' in txn_type else 0
    is_online = 1 if 'Online' in txn_type else 0
    is_pos = 1 if 'POS' in txn_type else 0
    is_transfer = 1 if 'Transfer' in txn_type else 0  # NEW!
    
    # Activity patterns
    high_daily_count = 1 if daily_count > 10 else 0
    low_daily_count = 1 if daily_count < 3 else 0  # NEW!
    
    # Failed transactions (CRITICAL - these were missing!)
    failed_count_7d = int(data.get('Failed_Transaction_Count_7d', 0))
    any_failed = 1 if failed_count_7d > 0 else 0
    high_failed = 1 if failed_count_7d > 2 else 0
    high_failed_count = 1 if failed_count_7d > 2 else 0  # Alias
    
    # Card features
    new_card = 1 if card_age < 30 else 0
    very_new_card = 1 if card_age < 15 else 0  # NEW!
    old_card = 1 if card_age > 180 else 0
    
    # Location
    far_transaction = 1 if txn_distance > 1000 else 0
    very_far = 1 if txn_distance > 3000 else 0
    local_transaction = 1 if txn_distance < 100 else 0  # NEW!
    suspicious_ip = ip_flag
    
    # Amount features
    amount_log = np.log1p(amount)
    balance_log = np.log1p(balance)
    large_amount = 1 if amount > 300 else 0
    very_large = 1 if amount > 1000 else 0  # NEW!
    small_amount = 1 if amount < 50 else 0  # NEW!
    low_balance = 1 if balance < 5000 else 0
    very_low_balance = 1 if balance < 1000 else 0  # NEW!
    
    # Combined patterns
    night_high_spend = 1 if (late_night and spend_ratio > 0.6) else 0
    night_large_amount = 1 if (late_night and large_amount) else 0
    distance_night = 1 if (far_transaction and late_night) else 0
    suspicious_combo = 1 if (suspicious_ip and late_night) else 0  # NEW!
    atm_night_far = 1 if (is_atm and late_night and far_transaction) else 0  # NEW!
    online_night = 1 if (is_online and late_night) else 0  # NEW!
    new_card_large = 1 if (new_card and large_amount) else 0  # NEW!
    weekend_night = 1 if (is_weekend and late_night) else 0  # NEW!
    velocity_alert = 1 if (high_daily_count and any_failed) else 0  # CRITICAL!
    
    # Create feature dict with ALL features
    all_features = {
        'Transaction_Amount': amount,
        'Account_Balance': balance,
        'spend_ratio': spend_ratio,
        'amount_vs_avg': amount_vs_avg,
        'amount_log': amount_log,
        'balance_log': balance_log,
        'Hour': hour,
        'DayOfWeek': day_of_week,
        'Is_Weekend': is_weekend,
        'late_night': late_night,
        'business_hours': business_hours,
        'early_morning': early_morning,
        'midnight': midnight,
        'is_atm': is_atm,
        'is_online': is_online,
        'is_pos': is_pos,
        'is_transfer': is_transfer,
        'Daily_Transaction_Count': daily_count,
        'high_daily_count': high_daily_count,
        'low_daily_count': low_daily_count,
        'Avg_Transaction_Amount_7d': avg_7d,
        'Failed_Transaction_Count_7d': failed_count_7d,  # ADDED!
        'any_failed': any_failed,  # ADDED!
        'high_failed': high_failed,  # ADDED!
        'high_failed_count': high_failed_count,  # ADDED!
        'Card_Age': card_age,
        'new_card': new_card,
        'very_new_card': very_new_card,
        'old_card': old_card,
        'Transaction_Distance': txn_distance,
        'far_transaction': far_transaction,
        'very_far': very_far,
        'local_transaction': local_transaction,
        'suspicious_ip': suspicious_ip,
        'large_amount': large_amount,
        'very_large': very_large,
        'small_amount': small_amount,
        'low_balance': low_balance,
        'very_low_balance': very_low_balance,
        'night_high_spend': night_high_spend,
        'night_large_amount': night_large_amount,
        'distance_night': distance_night,
        'suspicious_combo': suspicious_combo,
        'atm_night_far': atm_night_far,
        'online_night': online_night,
        'new_card_large': new_card_large,
        'weekend_night': weekend_night,
        'velocity_alert': velocity_alert  # ADDED!
    }
    
    # Create DataFrame
    df = pd.DataFrame([all_features])
    
    # Scale continuous features
    continuous = [
        'Transaction_Amount', 'Account_Balance',
        'spend_ratio', 'amount_vs_avg',
        'amount_log', 'balance_log',
        'Hour', 'DayOfWeek',
        'Daily_Transaction_Count', 'Avg_Transaction_Amount_7d',
        'Card_Age', 'Transaction_Distance'
    ]
    
    df_scaled = df.copy()
    for col in continuous:
        if col in df_scaled.columns:
            try:
                df_scaled[col] = scaler_bank.transform(df[[col]])
            except:
                pass
    
    # Return ONLY features model expects, in EXACT ORDER
    return df_scaled[features_bank]


def calculate_shap(model, features_df, top_n=5):
    """Calculate SHAP values"""
    try:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(features_df)
        
        if isinstance(shap_values, list):
            shap_values = shap_values[1]
        
        feature_importance = pd.DataFrame({
            'feature': features_df.columns,
            'shap_value': shap_values[0],
            'feature_value': features_df.iloc[0].values
        }).sort_values('shap_value', key=abs, ascending=False)
        
        top_features = []
        for idx, row in feature_importance.head(top_n).iterrows():
            top_features.append({
                'feature': row['feature'],
                'value': float(row['feature_value']),
                'shap_value': float(row['shap_value']),
                'impact': 'increases' if row['shap_value'] > 0 else 'decreases'
            })
        
        return top_features
    
    except Exception as e:
        print(f"SHAP Error: {e}")
        return []


def generate_ai_explanation(prediction, probability, top_features, amount):
    """Generate AI explanation"""
    
    risk = "CRITICAL" if probability >= 0.7 else "HIGH" if probability >= 0.5 else "MEDIUM" if probability >= 0.3 else "LOW" if probability >= 0.15 else "MINIMAL"
    
    if prediction == 1:
        explanation = f"⚠️ **FRAUD ALERT** ({probability*100:.1f}% confidence)\n\n"
        explanation += f"This ${amount:,.2f} transaction has been flagged as **{risk} RISK**.\n\n"
        explanation += "**Key Risk Factors:**\n"
        
        for feat in top_features[:3]:
            feat_name = feat['feature']
            feat_val = feat['value']
            
            if 'night' in feat_name.lower():
                explanation += f"• Late night transaction pattern detected\n"
            elif 'failed' in feat_name.lower():
                explanation += f"• Transaction failure history\n"
            elif 'distance' in feat_name.lower() and feat_val > 0:
                explanation += f"• Unusual transaction location\n"
            elif 'new_card' in feat_name.lower():
                explanation += f"• New card activity\n"
            else:
                explanation += f"• {feat_name}: {feat_val:.2f}\n"
        
        explanation += "\n**Recommendation:** Block or review this transaction immediately."
    
    else:
        explanation = f"✅ **Transaction Appears Normal** ({(1-probability)*100:.1f}% confidence)\n\n"
        explanation += f"This ${amount:,.2f} transaction shows **{risk} RISK** indicators.\n\n"
        explanation += "**Recommendation:** Transaction can proceed."
    
    return explanation


# ============================================
# API ENDPOINTS
# ============================================

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "healthy",
        "service": "Banking Fraud Detection",
        "model": "available",
        "features": len(features_bank),
        "threshold": threshold_bank
    })


@app.route("/predict", methods=["POST"])
@app.route("/api/check-fraud", methods=["POST"])
def predict():
    """Predict fraud"""
    try:
        data = request.get_json()
        
        # Prepare features
        features_df = prepare_features_bank(data)
        
        # Predict
        proba = model_bank.predict_proba(features_df)[0][1]
        pred = int(proba >= 0.5)
        
        # SHAP
        top_features = calculate_shap(model_bank, features_df)
        
        # Risk level
        if proba >= 0.7:
            risk = "CRITICAL"
        elif proba >= 0.5:
            risk = "HIGH"
        elif proba >= 0.4:
            risk = "MEDIUM"
        elif proba >= 0.2:
            risk = "LOW"
        else:
            risk = "MINIMAL"
        
        # Amount
        amount = float(data.get('Transaction_Amount', 0))
        
        # AI explanation
        ai_explanation = generate_ai_explanation(pred, proba, top_features, amount)
        
        # Response
        response = {
            "status": "success",
            "model_used": "Banking",
            "prediction": pred,
            "fraud_probability": float(proba),
            "risk_level": risk,
            "threshold": threshold_bank,
            "features_used": len(features_bank),
            "top_contributing_features": top_features,
            "ai_explanation": ai_explanation,
            "message": "⚠️ FRAUD DETECTED" if pred == 1 else "✅ Transaction Normal",
            "transaction_amount": amount
        }
        
        return jsonify(response)
        
    except Exception as e:
        import traceback
        return jsonify({
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }), 500


if __name__ == "__main__":
    print("🚀 Starting Server...")
    print("📍 http://localhost:5000\n")
    app.run(host="0.0.0.0", port=5000, debug=True)