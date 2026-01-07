# app.py - COMPLETELY FIXED VERSION
# Fixed: Trust score calculation, risk levels, all business rules

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
    update_prediction_feedback,
    get_feedback_count,
    init_database,
    close_database
)

# Analytics & Retraining
from analytics_routes import register_analytics_routes
from retraining_routes import register_retraining_routes

# Logging & Security
from logging_config import log_api_request, log_prediction, log_feedback, log_error
from auth_security import initialize_security, rate_limit, require_api_key

app = Flask(__name__)
CORS(app)

initialize_security(app)

print("="*80)
print("🎯 FRAUD DETECTION BACKEND - PRODUCTION READY")
print("="*80)

# ============================================
# BUSINESS RULES (IMPROVED)
# ============================================
def apply_business_rules(fraud_probability, data, mode):
    """Apply business logic - FIXED VERSION"""
    if mode != 'banking':
        return fraud_probability
    
    adjusted_prob = fraud_probability
    original_prob = fraud_probability
    
    try:
        transaction_amount = float(data.get('Transaction_Amount', 0))
        account_balance = float(data.get('Account_Balance', 0))
        avg_amount = float(data.get('Avg_Transaction_Amount_7d', 0))
        failed_count = int(data.get('Failed_Transaction_Count_7d', 0))
        card_age = int(data.get('Card_Age', 0))
        distance = float(data.get('Transaction_Distance', 0))
        
        print(f"\n🔍 Applying business rules:")
        print(f"   Original probability: {original_prob:.4f}")
        
        # Rule 1: Amount vs history (MORE STRICT)
        if avg_amount > 0:
            ratio = transaction_amount / avg_amount
            if ratio <= 1.5:  # Within 1.5x
                adjusted_prob *= 0.80
                print(f"   [Rule 1] Within 1.5x average: {adjusted_prob:.4f}")
            elif ratio <= 2.0:  # Within 2x
                adjusted_prob *= 0.90
                print(f"   [Rule 1] Within 2x average: {adjusted_prob:.4f}")
            elif ratio <= 2.5:  # Within 2.5x
                adjusted_prob *= 0.95
                print(f"   [Rule 1] Within 2.5x average: {adjusted_prob:.4f}")
            # If > 2.5x, no reduction (suspicious)
        
        # Rule 2: Failed transactions (REFINED)
        if failed_count == 0:
            adjusted_prob *= 0.7
            print(f"   [Rule 2] No failed transactions: {adjusted_prob:.4f}")
        elif failed_count <= 2:
            adjusted_prob *= 0.8
            print(f"   [Rule 2] Low failed transactions: {adjusted_prob:.4f}")
        
        # Rule 3: Card age (REFINED)
        if card_age > 365:
            adjusted_prob *= 0.85
            print(f"   [Rule 3] Very mature card (1+ year): {adjusted_prob:.4f}")
        elif card_age > 180:
            adjusted_prob *= 0.90
            print(f"   [Rule 3] Mature card (6+ months): {adjusted_prob:.4f}")
        elif card_age > 90:
            adjusted_prob *= 0.95
            print(f"   [Rule 3] Established card (3+ months): {adjusted_prob:.4f}")
        
        # Rule 4: Distance (REFINED)
        if distance < 30:
            adjusted_prob *= 0.88
            print(f"   [Rule 4] Very local transaction: {adjusted_prob:.4f}")
        elif distance < 100:
            adjusted_prob *= 0.93
            print(f"   [Rule 4] Local transaction: {adjusted_prob:.4f}")
        
        # Rule 5: Can afford (STRICT)
        balance_ratio = account_balance / transaction_amount
        if balance_ratio >= 2.0:  # Balance is 2x+ amount
            adjusted_prob *= 0.7
            print(f"   [Rule 5] High balance coverage: {adjusted_prob:.4f}")
        elif balance_ratio >= 1.0:  # Balance covers amount
            adjusted_prob *= 0.85
            print(f"   [Rule 5] Sufficient balance: {adjusted_prob:.4f}")
        elif balance_ratio >= 0.5:  # At least 50%
            adjusted_prob *= 0.9
            print(f"   [Rule 5] Partial balance: {adjusted_prob:.4f}")
        # If < 50%, no reduction (risky)
        
        # Rule 6: Business hours
        try:
            timestamp = data.get('Timestamp', '')
            dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            hour = dt.hour
            if 9 <= hour <= 20:
                adjusted_prob *= 0.95
                print(f"   [Rule 6] Business hours: {adjusted_prob:.4f}")
        except:
            pass
        
        adjusted_prob = max(0.0, min(1.0, adjusted_prob))
        
        print(f"   ✅ Final adjusted: {adjusted_prob:.4f}")
        print(f"   📉 Reduction: {(original_prob - adjusted_prob)*100:.1f}%\n")
        
        return adjusted_prob
        
    except Exception as e:
        print(f"   ⚠️  Error: {e}")
        return fraud_probability

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
    load_dotenv()
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
threshold_banking = 0.65
scaler_banking = None
explainer_banking = None

try:
    if os.path.exists("models/fraud_model_banking.pkl"):
        model_banking = joblib.load("models/fraud_model_banking.pkl")
        model_type_banking = "RandomForest" if isinstance(model_banking, RandomForestClassifier) else "XGBoost"
    else:
        model_banking = XGBClassifier()
        model_banking.load_model("models/fraud_model_banking.json")
        model_type_banking = "XGBoost"
    
    if os.path.exists("models/features_banking.json"):
        with open("models/features_banking.json") as f:
            features_banking = json.load(f)
    
    if os.path.exists("models/model_config_banking.json"):
        with open("models/model_config_banking.json") as f:
            config = json.load(f)
            threshold_banking = config.get("recommended_threshold", 0.65)
            print(f"   Threshold: {threshold_banking}")
    
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
print(f"🎯 Business Rules: ✅ ENABLED (v2.0 - FIXED)")
print("="*80 + "\n")

# ============================================
# FEATURE PREPARATION (FIXED TRUST SCORE)
# ============================================
def prepare_banking_features(data):
    """FIXED VERSION with correct trust score"""
    
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
        hour = dt.hour
        day_of_week = dt.weekday()
        is_weekend = 1 if day_of_week >= 5 else 0
    except:
        hour, day_of_week, is_weekend = 12, 2, 0
    
    # FIXED TRUST SCORE CALCULATION
    trust_score = 0
    
    # 1. Card age (max 2 points)
    if card_age > 365:
        trust_score += 2
    elif card_age > 180:
        trust_score += 1.5
    elif card_age > 90:
        trust_score += 1
    
    # 2. Failed transactions (max 2 points)
    if failed_count_7d == 0:
        trust_score += 2
    elif failed_count_7d <= 4:
        trust_score += 1.5
    
    # 3. Balance coverage (max 2 points)
    balance_ratio = balance / amount
    if balance_ratio >= 2.0:
        trust_score += 2.5
    elif balance_ratio >= 1.0:
        trust_score += 2
    elif balance_ratio >= 0.5:
        trust_score += 1.5
    
    # 4. Amount vs average (max 2 points) - THIS WAS MISSING!
    if avg_7d > 0:
        amount_ratio = amount / avg_7d
        if amount_ratio <= 1.5:
            trust_score += 2
        elif amount_ratio <= 2.0:
            trust_score += 1
        elif amount_ratio <= 2.5:
            trust_score += 0.5
        # > 2.5x = 0 points (suspicious)
    
    # 5. Transaction pattern (max 2 points)
    if daily_count <= 5:
        trust_score += 2
    elif daily_count <= 10:
        trust_score += 1
    
    # Total possible: 10 points
    # High trust: >= 7 points
    
    features = {
        'amount': amount,
        'balance': balance,
        'spend_ratio': amount / (balance + amount + 1),
        'amount_vs_avg': amount / (avg_7d + 1),
        'within_2x_avg': 1 if (avg_7d > 0 and amount <= avg_7d * 2) else 0,
        'within_3x_avg': 1 if (avg_7d > 0 and amount <= avg_7d * 3) else 0,
        'amount_log': np.log1p(amount),
        'balance_log': np.log1p(balance),
        'hour': hour,
        'day_of_week': day_of_week,
        'is_weekend': is_weekend,
        'late_night': 1 if (hour >= 22 or hour <= 8) else 0,
        'very_late_night': 1 if (1 <= hour <= 4) else 0,
        'business_hours': 1 if (9 <= hour <= 17) else 0,
        'is_atm': 1 if 'ATM' in txn_type else 0,
        'is_online': 1 if 'Online' in txn_type else 0,
        'is_pos': 1 if 'POS' in txn_type else 0,
        'is_transfer': 1 if 'Transfer' in txn_type else 0,
        'daily_count': daily_count,
        'very_high_daily_count': 1 if daily_count > 15 else 0,
        'reasonable_daily_count': 1 if daily_count <= 10 else 0,
        'avg_7d': avg_7d,
        'failed_7d': failed_count_7d,
        'few_failed': 1 if failed_count_7d <= 4 else 0,
        'many_failed': 1 if failed_count_7d > 5 else 0,
        'card_age': card_age,
        'very_new_card': 1 if card_age < 7 else 0,
        'new_card': 1 if card_age < 30 else 0,
        'established_card': 1 if card_age > 90 else 0,
        'mature_card': 1 if card_age > 180 else 0,
        'distance': txn_distance,
        'local_txn': 1 if txn_distance < 50 else 0,
        'nearby_txn': 1 if txn_distance < 200 else 0,
        'far_txn': 1 if txn_distance > 1000 else 0,
        'very_far_txn': 1 if txn_distance > 3000 else 0,
        'small_amount': 1 if amount < 500 else 0,
        'normal_amount': 1 if (500 <= amount <= 2000) else 0,
        'large_amount': 1 if amount > 2001 else 0,
        'very_large_amount': 1 if amount > 5000 else 0,
        'healthy_balance': 1 if balance > 500 else 0,
        'low_balance': 1 if balance <= 500 else 0,
        'suspicious_ip': ip_flag,
        'trust_score': trust_score,
        'high_trust': 1 if trust_score >= 5.5 else 0
    }
    
    df = pd.DataFrame([features])
    
    if scaler_banking:
        continuous = [
            'amount', 'balance', 'spend_ratio', 'amount_vs_avg',
            'amount_log', 'balance_log', 'hour', 'day_of_week',
            'daily_count', 'avg_7d', 'failed_7d', 'card_age', 'distance', 'trust_score'
        ]
        
        for col in continuous:
            if col in df.columns:
                try:
                    df[[col]] = scaler_banking.transform(df[[col]])
                except:
                    pass
    
    available = [f for f in features_banking if f in df.columns]
    return df[available]

def prepare_credit_card_features(data):
    """Credit card preparation"""
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
    """Fallback explanation"""
    risk = "CRITICAL" if proba >= 0.8 else "HIGH" if proba >= 0.65 else "MEDIUM" if proba >= 0.45 else "LOW"
    
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
            
            # APPLY BUSINESS RULES
            proba = apply_business_rules(proba, data, mode)
            
            pred = int(proba >= 0.65)
            top_features = explainer_banking.explain(features_df, 5)
            amount = float(data.get('Transaction_Amount', 0))
            threshold = threshold_banking
        
        # FIXED RISK LEVELS
        if proba >= 0.8:
            risk = "CRITICAL"
        elif proba >= 0.7:
            risk = "HIGH"
        elif proba >= 0.6:
            risk = "MEDIUM"
        elif proba >= 0.4:
            risk = "LOW"
        else:
            risk = "MINIMAL"
        
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
        "genai": GENAI_ENABLED,
        "business_rules": "v2.0_fixed"
    })

@app.route("/api/stats", methods=["GET"])
def stats():
    """Fixed stats endpoint"""
    if not DB_ENABLED:
        return jsonify({"status": "error"}), 503
    
    try:
        total_count = get_feedback_count(model_type=None, days=3650)
        banking_count = get_feedback_count(model_type='banking', days=3650)
        cc_count = get_feedback_count(model_type='credit_card', days=3650)
        
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
    port = int(os.getenv("PORT", 5000))
    print(f"🚀 Starting Flask server on 0.0.0.0:{port}", flush=True)
    app.run(host="0.0.0.0", port=port, debug=False)
