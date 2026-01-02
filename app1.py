# app.py - FINAL FIXED VERSION
# Issues fixed:
# 1. Stats API now counts feedback correctly
# 2. API authentication enforced when key present
# 3. GET prediction endpoint added

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
import threading

# Database
from database.db_dual import (
    save_prediction_to_db,
    get_prediction_by_id,
    get_recent_predictions,
    update_prediction_feedback,
    get_feedback_count,
    init_database,
    close_database
)

# Analytics & Retraining
from analytics_routes import register_analytics_routes
from retraining_routes import register_retraining_routes

# Phase 6: Logging & Security
from logging_config import (
    log_api_request, log_prediction, log_feedback, log_error
)
from auth_security import (
    initialize_security, rate_limit,
    validate_banking_input, validate_credit_card_input,
     require_api_key  # ADD THIS
)

app = Flask(__name__)
CORS(app)

# Initialize Security
initialize_security(app)

print("="*80)
print("🎯 FRAUD DETECTION BACKEND - PRODUCTION READY")
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
        from genai import explain_transaction
except:
    GENAI_ENABLED = False

# ============================================
# LOAD MODELS
# ============================================
model_banking = None
features_banking = None
threshold_banking = 0.45
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
    
    if os.path.exists("models/features_banking.json"):
        with open("models/features_banking.json") as f:
            features_banking = json.load(f)
    else:
        features_banking = [
            'Transaction_Amount', 'Account_Balance', 'spend_ratio', 'amount_vs_avg',
            'amount_log', 'balance_log', 'Hour', 'DayOfWeek', 'Is_Weekend',
            'late_night', 'business_hours', 'early_morning', 'midnight',
            'is_atm', 'is_online', 'is_pos', 'is_transfer',
            'Daily_Transaction_Count', 'high_daily_count', 'low_daily_count', 'moderate_daily_count',
            'Avg_Transaction_Amount_7d', 'Failed_Transaction_Count_7d', 'any_failed',
            'high_failed', 'high_failed_count', 'Card_Age', 'new_card', 'very_new_card', 'old_card',
            'Transaction_Distance', 'far_transaction', 'very_far', 'local_transaction',
            'moderate_distance', 'suspicious_ip', 'large_amount', 'very_large',
            'small_amount', 'moderate_amount', 'low_balance', 'very_low_balance',
            'night_high_spend', 'night_large_amount', 'distance_night', 'suspicious_combo',
            'atm_night_far', 'online_night', 'new_card_large', 'weekend_night',
            'velocity_alert', 'distance_alert'
        ]
    
    if os.path.exists("models/model_config_banking.json"):
        with open("models/model_config_banking.json") as f:
            threshold_banking = json.load(f).get("default_threshold", 0.3)
    
    if os.path.exists("models/scaler_banking.pkl"):
        scaler_banking = joblib.load("models/scaler_banking.pkl")
    
    explainer_banking = SimpleExplainer(model_banking, features_banking)
    print(f"✅ BANKING: {model_type_banking} ({len(features_banking)} features)")
    
except Exception as e:
    print(f"⚠️  BANKING: {e}")
    model_banking = None

model_cc = None
features_cc = None
threshold_cc = 0.45
explainer_cc = None

try:
    model_cc = XGBClassifier()
    model_cc.load_model("models/fraud_model_final.json")
    
    if os.path.exists("models/features.json"):
        with open("models/features.json") as f:
            features_cc = json.load(f)
    elif os.path.exists("models/model_config.json"):
        with open("models/model_config.json") as f:
            config = json.load(f)
            features_cc = config.get('features', [])
    else:
        features_cc = ['Time', 'Amount'] + [f'V{i}' for i in range(1, 29)] + [
            'Hour', 'time_gap', 'txn_last_1hr', 'Amount_log',
            'amount_roll_mean_3', 'amount_roll_std_3'
        ]
    
    if os.path.exists("models/model_config.json"):
        with open("models/model_config.json") as f:
            config = json.load(f)
            threshold_cc = config.get("default_threshold", 0.4)
    
    explainer_cc = SimpleExplainer(model_cc, features_cc)
    print(f"✅ CREDIT_CARD: XGBoost ({len(features_cc)} features)")
    
except Exception as e:
    print(f"⚠️  CREDIT_CARD: {e}")
    model_cc = None

DB_ENABLED = init_database()

if DB_ENABLED:
    register_analytics_routes(app)
    register_retraining_routes(app)

print("="*80)
print(f"🤖 GenAI: {'✅ ENABLED' if GENAI_ENABLED else '⚠️  FALLBACK'}")
print(f"🗄️  Database: {'✅ ENABLED' if DB_ENABLED else '❌ DISABLED'}")
print(f"📊 Logging: ✅ ENABLED")
print(f"🔒 Security: ✅ RATE LIMITING + VALIDATION")
print(f"🔄 Auto-Retrain: ✅ AT 50 FEEDBACKS")
print("="*80 + "\n")

# ============================================
# FEATURE PREPARATION (keeping your code)
# ============================================
def prepare_banking_features(data):
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
    
    available = [f for f in features_banking if f in df_scaled.columns]
    return df_scaled[available]

def prepare_credit_card_features(data):
    features = {}
    for i in range(1, 29):
        v_key = f'V{i}'
        if v_key not in data:
            raise ValueError(f"Missing {v_key}")
        features[v_key] = float(data[v_key])
    
    features['Amount'] = float(data.get('Amount', 0))
    features['Time'] = float(data.get('Time', 0))
    
    hour = (features['Time'] / 3600) % 24
    features['Hour'] = hour
    features['time_gap'] = 0
    features['txn_last_1hr'] = 1
    features['Amount_log'] = np.log1p(features['Amount'])
    features['amount_roll_mean_3'] = features['Amount']
    features['amount_roll_std_3'] = 0
    
    df = pd.DataFrame([features])
    available = [f for f in features_cc if f in df.columns]
    return df[available]

def generate_fallback(pred, proba, top_features, amount):
    risk = "CRITICAL" if proba >= 0.7 else "HIGH" if proba >= 0.5 else "MEDIUM" if proba >= 0.3 else "LOW"
    
    if pred == 1:
        exp = f"⚠️ FRAUD ALERT ({proba*100:.1f}% confidence)\n\n"
        exp += f"${amount:.2f} flagged as {risk} RISK.\n\nKey factors:\n"
        for f in top_features[:3]:
            exp += f"• {f['feature']}: {f['value']:.2f}\n"
        exp += "\nRecommendation: Block/review."
    else:
        exp = f"✅ Normal Transaction ({(1-proba)*100:.1f}% confidence)\n\n"
        exp += f"${amount:.2f} shows {risk} risk.\nRecommendation: Approve."
    
    return exp

# ============================================
# API ENDPOINTS
# ============================================
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "healthy",
        "database": "connected" if DB_ENABLED else "disconnected",
        "modes": {
            "banking": model_banking is not None,
            "credit_card": model_cc is not None
        }
    })

@app.route("/api/check-fraud", methods=["POST"])
@rate_limit
@require_api_key
def check_fraud():
    try:
        data = request.get_json()
        mode = data.get('mode', 'banking').lower()
        
        log_api_request('/api/check-fraud', 'POST', request.remote_addr, params={'mode': mode})
        
        original_data = data.copy()
        
        if mode == 'credit_card':
            if not model_cc:
                return jsonify({"status": "error", "message": "Credit card model unavailable"}), 400
            
            features_df = prepare_credit_card_features(data)
            proba = model_cc.predict_proba(features_df)[0][1]
            pred = int(proba >= threshold_cc)
            top_features = explainer_cc.explain(features_df, 5)
            amount = float(data.get('Amount', 0))
            threshold = threshold_cc
            
        else:
            if not model_banking:
                return jsonify({"status": "error", "message": "Banking model unavailable"}), 400
            
            features_df = prepare_banking_features(data)
            proba = model_banking.predict_proba(features_df)[0][1]
            pred = int(proba >= threshold_banking)
            top_features = explainer_banking.explain(features_df, 5)
            amount = float(data.get('Transaction_Amount', 0))
            threshold = threshold_banking
        
        risk = "HIGH" if proba >= 0.7 else "MEDIUM" if proba >= 0.4 else "LOW"
        
        if GENAI_ENABLED:
            try:
                ai_exp = explain_transaction(top_features, proba, amount, mode)
            except:
                ai_exp = generate_fallback(pred, proba, top_features, amount)
        else:
            ai_exp = generate_fallback(pred, proba, top_features, amount)
        
        response = {
            "status": "success",
            "prediction": pred,
            "is_fraud": bool(pred == 1),
            "fraud_probability": round(float(proba), 4),
            "risk_level": risk,
            "mode": mode,
            "explanation": ai_exp,
            "timestamp": datetime.now().isoformat()
        }
        
        if DB_ENABLED:
            try:
                db_data = {
                    'mode': mode,
                    'prediction': pred,
                    'fraud_probability': float(proba),
                    'risk_level': risk,
                    'threshold_used': threshold,
                    'top_features': top_features,
                    'ai_explanation': ai_exp,
                    'ai_provider': 'groq' if GENAI_ENABLED else 'fallback',
                    'api_endpoint': '/api/check-fraud',
                    'request_ip': request.remote_addr,
                    **original_data
                }
                
                prediction_id = save_prediction_to_db(db_data)
                if prediction_id:
                    response['prediction_id'] = prediction_id
                    log_prediction(prediction_id, mode, pred, proba, request.remote_addr)
            except Exception as e:
                log_error('DB_SAVE_ERROR', str(e))
        
        return jsonify(response)
        
    except Exception as e:
        log_error('PREDICTION_ERROR', str(e), exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/predictions/<int:prediction_id>/feedback", methods=["POST"])
@rate_limit
def submit_feedback(prediction_id):
    if not DB_ENABLED:
        return jsonify({"status": "error", "message": "Database not available"}), 503
    
    try:
        data = request.get_json()
        actual_class = data.get('actual_class')
        feedback_note = data.get('feedback_note', '')
        
        log_api_request(f'/api/predictions/{prediction_id}/feedback', 'POST', request.remote_addr)
        
        if actual_class not in [0, 1]:
            return jsonify({"status": "error", "message": "actual_class must be 0 or 1"}), 400
        
        success = update_prediction_feedback(prediction_id, actual_class, feedback_note)
        
        if success:
            log_feedback(prediction_id, actual_class, 'recorded')
            
            def check_retrain():
                try:
                    from retraining_routes import auto_trigger_retraining
                    auto_trigger_retraining()
                except Exception as e:
                    print(f"⚠️  Auto-retrain check: {e}")
            
            threading.Thread(target=check_retrain, daemon=True).start()
            
            return jsonify({
                "status": "success",
                "message": "Feedback recorded. Thank you!",
                "prediction_id": prediction_id
            })
        else:
            return jsonify({"status": "error", "message": "Failed to record"}), 500
            
    except Exception as e:
        log_error('FEEDBACK_ERROR', str(e), exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/predictions/<int:prediction_id>", methods=["GET"])
def get_prediction_detail(prediction_id):
    if not DB_ENABLED:
        return jsonify({"status": "error", "message": "Database not available"}), 503
    
    try:
        prediction = get_prediction_by_id(prediction_id)
        
        if not prediction:
            return jsonify({"status": "error", "message": "Prediction not found"}), 404
        
        return jsonify({
            "status": "success",
            "prediction": {
                "id": prediction.get('id'),
                "model_type": prediction.get('model_type'),
                "prediction": prediction.get('prediction'),
                "fraud_probability": float(prediction.get('fraud_probability', 0)),
                "risk_level": prediction.get('risk_level'),
                "actual_class": prediction.get('actual_class'),
                "has_feedback": prediction.get('actual_class') is not None,
                "predicted_at": str(prediction.get('predicted_at')) if prediction.get('predicted_at') else None,
                "feedback_received_at": str(prediction.get('feedback_received_at')) if prediction.get('feedback_received_at') else None
            }
        })
    except Exception as e:
        log_error('GET_PREDICTION_ERROR', str(e), exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "models": {
            "banking": model_banking is not None,
            "credit_card": model_cc is not None
        },
        "database": DB_ENABLED,
        "genai": GENAI_ENABLED
    })

@app.route("/api/stats", methods=["GET"])
def stats():
    """FIXED: Now counts feedback correctly from database"""
    if not DB_ENABLED:
        return jsonify({"status": "error"}), 503
    
    try:
        # Use database function directly instead of get_recent_predictions
        total_count = get_feedback_count(model_type=None, days=3650)  # All time
        banking_count = get_feedback_count(model_type='banking', days=3650)
        cc_count = get_feedback_count(model_type='credit_card', days=3650)
        
        # Get total predictions via database query
        from database.db_dual import db
        with db.get_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as total FROM predictions")
            total_predictions = cursor.fetchone()['total']
        
        return jsonify({
            "status": "success",
            "total_predictions": total_predictions,
            "with_feedback": total_count,
            "feedback_rate": round((total_count / total_predictions * 100) if total_predictions > 0 else 0, 2),
            "by_model": {
                "banking": banking_count,
                "credit_card": cc_count
            }
        })
    except Exception as e:
        log_error('STATS_ERROR', str(e), exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500

@app.teardown_appcontext
def shutdown(exception=None):
    if DB_ENABLED:
        close_database()

if __name__ == "__main__":
    print("🚀 Server: http://localhost:5000\n")
    app.run(host="0.0.0.0", port=5000, debug=True)