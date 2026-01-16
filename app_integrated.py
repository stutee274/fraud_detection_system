# app_integrated.py - Complete Integrated Fraud Detection System
"""
✅ Dual Mode: Banking + Credit Card
✅ Database: PostgreSQL with prediction tracking
✅ Feedback: User feedback collection
✅ Analytics: Dashboard statistics
✅ Retraining: Auto-retraining when feedback threshold reached
✅ Security: API key authentication and rate limiting
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from xgboost import XGBClassifier
import json
import joblib
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# CORS Configuration for Production
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:3000",
            "https://frauddetectionsystem-production.up.railway.app",
            "https://fraud-detection-system-snowy.vercel.app",
            "https://*.vercel.app",
            "https://*.netlify.app",
            "*"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "X-API-Key", "Authorization"],
        "supports_credentials": True,
        "expose_headers": ["Content-Type", "X-API-Key"]
    }
})

print("="*80)
print(" INTEGRATED FRAUD DETECTION SYSTEM")
print("="*80)

# ============================================
# LOAD BANKING MODEL
# ============================================
model_banking = None
features_banking = None
threshold_banking = 0.55
scaler_banking = None

try:
    temp_model = XGBClassifier()
    temp_model.load_model("models/fraud_model_banking.json")
    
    with open("models/features_banking.json") as f:
        features_banking = json.load(f)
    
    with open("models/model_config_banking.json") as f:
        threshold_banking = json.load(f).get("default_threshold", 0.55)
    
    # Try loading scaler, but don't fail hard if missing (just warn)
    try:
        scaler_banking = joblib.load("models/scaler_banking.pkl")
    except:
        print("⚠️  BANKING Model: Scaler not found (using unscaled values)")
        scaler_banking = None
        
    model_banking = temp_model
    print(f"✅ BANKING Model: XGBoost ({len(features_banking)} features)")
    print(f"   Threshold: {threshold_banking}")
    
except Exception as e:
    model_banking = None
    features_banking = None
    print(f"⚠️  BANKING Model: Not available ({e})")

# ============================================
# LOAD CREDIT CARD MODEL
# ============================================
model_cc = None
features_cc = None
threshold_cc = 0.4

try:
    temp_model = XGBClassifier()
    temp_model.load_model("models/fraud_model_final.json")
    
    loaded_features = None
    if os.path.exists("models/features.json"):
        with open("models/features.json") as f:
            loaded_features = json.load(f)
    elif os.path.exists("models/features.json"):
        with open("models/features.json") as f:
            loaded_features = json.load(f)
            
    if loaded_features:
        features_cc = loaded_features
        model_cc = temp_model
        
        if os.path.exists("models/model_config.json"):
            with open("models/model_config.json") as f:
                config = json.load(f)
                threshold_cc = config.get("default_threshold", 0.4)
        
        print(f"✅ CREDIT_CARD Model: XGBoost ({len(features_cc)} features)")
        print(f"   Threshold: {threshold_cc}")
    else:
        print("⚠️  CREDIT_CARD Model: Features file missing")
        model_cc = None
    
except Exception as e:
    model_cc = None
    features_cc = None
    print(f"⚠️  CREDIT_CARD Model: Not available ({e})")
    print(f"⚠️  CREDIT_CARD Model: Not available ({e})")

# ============================================
# LOAD DATABASE
# ============================================
DB_ENABLED = False
try:
    from database.db_dual import (
        init_database,
        close_database,
        save_prediction_to_db,
        get_prediction_by_id,
        get_recent_predictions,
        update_prediction_feedback,
        get_feedback_count
    )
    
    DB_ENABLED = init_database()
    if DB_ENABLED:
        print("✅ Database: CONNECTED")
    else:
        print("⚠️  Database: DISABLED (continuing without DB)")
except Exception as e:
    print(f"⚠️  Database: DISABLED ({e})")

# ============================================
# LOAD ANALYTICS & RETRAINING
# ============================================
try:
    from analytics_routes import register_analytics_routes
    from retraining_routes import register_retraining_routes, auto_trigger_retraining
    
    register_analytics_routes(app)
    register_retraining_routes(app)
    print("✅ Analytics & Retraining: ENABLED")
except Exception as e:
    print(f"⚠️  Analytics & Retraining: DISABLED ({e})")
    auto_trigger_retraining = None

# ============================================
# LOAD GENAI
# ============================================
GENAI_ENABLED = False
try:
    from genai import explain_transaction
    GENAI_ENABLED = True
    print(" GenAI: ENABLED")
except Exception as e:
    print(f" GenAI: DISABLED ({e})")

print("="*80 + "\n")

# ============================================
# FEATURE ENGINEERING - BANKING
# ============================================
def prepare_banking_features(data):
    """Prepare banking features matching train_banking.py"""
    # Raw inputs
    amount_val = float(data.get('Transaction_Amount', 0))
    balance_val = float(data.get('Account_Balance', 0))
    timestamp = data.get('Timestamp', '')
    txn_type = data.get('Transaction_Type', 'POS')
    daily_count_val = int(data.get('Daily_Transaction_Count', 1))
    avg_7d_val = float(data.get('Avg_Transaction_Amount_7d', amount_val))
    failed_7d_val = int(data.get('Failed_Transaction_Count_7d', 0))
    card_age_val = int(data.get('Card_Age', 100))
    distance_val = float(data.get('Transaction_Distance', 500))
    ip_flag_val = int(data.get('IP_Address_Flag', 0))

    # Time features
    try:
        dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        hour = dt.hour
        day_of_week = dt.weekday()
    except:
        hour = 12
        day_of_week = 2
    
    is_weekend = 1 if day_of_week >= 5 else 0

    # Amount features
    amount = amount_val
    balance = balance_val
    spend_ratio = amount / (balance + amount + 1)

    # Historical
    avg_7d = avg_7d_val
    amount_vs_avg = amount / (avg_7d + 1)
    within_2x_avg = 1 if amount <= (avg_7d * 2) else 0
    within_3x_avg = 1 if amount <= (avg_7d * 3) else 0

    # Log transforms
    amount_log = np.log1p(amount)
    balance_log = np.log1p(balance)

    # Time patterns
    late_night = 1 if (hour >= 23 or hour <= 5) else 0
    very_late_night = 1 if (hour >= 1 and hour <= 4) else 0
    business_hours = 1 if (hour >= 9 and hour <= 17) else 0

    # Txn type
    is_atm = 1 if 'ATM' in txn_type.upper() else 0
    is_online = 1 if 'ONLINE' in txn_type.upper() else 0
    is_pos = 1 if 'POS' in txn_type.upper() else 0
    is_transfer = 1 if 'TRANSFER' in txn_type.upper() else 0

    # Activity
    daily_count = daily_count_val
    very_high_daily_count = 1 if daily_count > 15 else 0
    reasonable_daily_count = 1 if daily_count <= 10 else 0

    # Failed
    failed_7d = failed_7d_val
    few_failed = 1 if failed_7d <= 2 else 0
    many_failed = 1 if failed_7d > 5 else 0

    # Card Age
    card_age = card_age_val
    very_new_card = 1 if card_age < 7 else 0
    new_card = 1 if card_age < 30 else 0
    established_card = 1 if card_age > 90 else 0
    mature_card = 1 if card_age > 180 else 0

    # Distance
    distance = distance_val
    local_txn = 1 if distance < 50 else 0
    nearby_txn = 1 if distance < 200 else 0
    far_txn = 1 if distance > 1000 else 0
    very_far_txn = 1 if distance > 3000 else 0

    # Categories
    small_amount = 1 if amount < 100 else 0
    normal_amount = 1 if (amount >= 100 and amount <= 500) else 0
    large_amount = 1 if amount > 500 else 0
    very_large_amount = 1 if amount > 2000 else 0

    healthy_balance = 1 if balance > 5000 else 0
    low_balance = 1 if balance < 1000 else 0

    suspicious_ip = ip_flag_val

    # Trust Score
    trust_score = (
        established_card +
        few_failed +
        (1 if balance >= amount else 0) +
        within_2x_avg +
        reasonable_daily_count
    )
    high_trust = 1 if trust_score >= 4 else 0

    # Construct dict
    features = {
        'amount': amount, 'balance': balance, 'spend_ratio': spend_ratio, 
        'amount_vs_avg': amount_vs_avg, 'within_2x_avg': within_2x_avg, 
        'within_3x_avg': within_3x_avg, 'amount_log': amount_log, 
        'balance_log': balance_log, 'hour': hour, 'day_of_week': day_of_week, 
        'is_weekend': is_weekend, 'late_night': late_night, 
        'very_late_night': very_late_night, 'business_hours': business_hours,
        'is_atm': is_atm, 'is_online': is_online, 'is_pos': is_pos, 
        'is_transfer': is_transfer, 'daily_count': daily_count, 
        'very_high_daily_count': very_high_daily_count, 
        'reasonable_daily_count': reasonable_daily_count, 'avg_7d': avg_7d, 
        'failed_7d': failed_7d, 'few_failed': few_failed, 'many_failed': many_failed,
        'card_age': card_age, 'very_new_card': very_new_card, 
        'new_card': new_card, 'established_card': established_card, 
        'mature_card': mature_card, 'distance': distance, 'local_txn': local_txn, 
        'nearby_txn': nearby_txn, 'far_txn': far_txn, 'very_far_txn': very_far_txn,
        'small_amount': small_amount, 'normal_amount': normal_amount, 
        'large_amount': large_amount, 'very_large_amount': very_large_amount,
        'healthy_balance': healthy_balance, 'low_balance': low_balance,
        'suspicious_ip': suspicious_ip, 'trust_score': trust_score, 
        'high_trust': high_trust
    }

    df = pd.DataFrame([features])
    
    # Scale
    continuous = [
        'amount', 'balance', 'spend_ratio', 'amount_vs_avg',
        'amount_log', 'balance_log', 'hour', 'day_of_week',
        'daily_count', 'avg_7d', 'failed_7d', 'card_age', 'distance', 'trust_score'
    ]
    
    if scaler_banking:
         try:
             df[continuous] = scaler_banking.transform(df[continuous])
         except Exception as e:
             print(f"Scaling error: {e}")
    
    # Return features in correct order
    final_df = pd.DataFrame()
    for col in features_banking:
        if col in df.columns:
            final_df[col] = df[col]
        else:
            final_df[col] = 0
            
    return final_df

# ============================================
# FEATURE ENGINEERING - CREDIT CARD
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

# Create explainers
explainer_banking = SimpleExplainer(model_banking, features_banking) if model_banking else None
explainer_cc = SimpleExplainer(model_cc, features_cc) if model_cc else None

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
# MAIN PREDICTION ENDPOINT
# ============================================
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "healthy",
        "service": "Integrated Fraud Detection System",
        "modes": {
            "banking": {
                "available": model_banking is not None,
                "features": len(features_banking) if features_banking else 0
            },
            "credit_card": {
                "available": model_cc is not None,
                "features": len(features_cc) if features_cc else 0
            }
        },
        "database": DB_ENABLED,
        "genai": GENAI_ENABLED
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
            pred = int(proba >= threshold_cc)
            top_features = explainer_cc.explain(features_df, 5) if explainer_cc else []
            amount = float(data.get('Amount', 0))
            threshold = threshold_cc
            model_name = "Credit Card (V1-V28)"
            
        else:
            # BANKING MODE (default)
            if not model_banking:
                return jsonify({"status": "error", "message": "Banking model unavailable"}), 400
            
            features_df = prepare_banking_features(data)
            proba = model_banking.predict_proba(features_df)[0][1]
            pred = int(proba >= threshold_banking)
            top_features = explainer_banking.explain(features_df, 5) if explainer_banking else []
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
        
        # Save to database
        prediction_id = None
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
                    **data  # Include all original data
                }
                
                prediction_id = save_prediction_to_db(db_data)
            except Exception as e:
                print(f"❌ Error saving to database: {e}")
        
        response = {
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
        }
        
        if prediction_id:
            response['prediction_id'] = prediction_id
        
        return jsonify(response)
        
    except Exception as e:
        import traceback
        return jsonify({"status": "error", "message": str(e), "trace": traceback.format_exc()}), 500

# ============================================
# DATABASE ENDPOINTS
# ============================================
@app.route("/api/predictions/<int:prediction_id>", methods=["GET"])
def get_prediction(prediction_id):
    """Get prediction by ID"""
    if not DB_ENABLED:
        return jsonify({"status": "error", "message": "Database not available"}), 503
    
    try:
        prediction = get_prediction_by_id(prediction_id)
        
        if prediction:
            return jsonify({
                "status": "success",
                "prediction": prediction
            })
        else:
            return jsonify({
                "status": "error",
                "message": "Prediction not found"
            }), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/predictions", methods=["GET"])
def get_predictions():
    """Get recent predictions"""
    if not DB_ENABLED:
        return jsonify({"status": "error", "message": "Database not available"}), 503
    
    try:
        limit = request.args.get('limit', 50, type=int)
        predictions = get_recent_predictions(limit)
        
        return jsonify({
            "status": "success",
            "count": len(predictions),
            "predictions": predictions
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/predictions/<int:prediction_id>/feedback", methods=["POST"])
def submit_feedback(prediction_id):
    """Submit feedback for a prediction"""
    if not DB_ENABLED:
        return jsonify({"status": "error", "message": "Database not available"}), 503
    
    try:
        data = request.get_json()
        actual_class = data.get('actual_class')
        feedback_note = data.get('feedback_note', '')
        
        if actual_class not in [0, 1]:
            return jsonify({
                "status": "error",
                "message": "actual_class must be 0 (normal) or 1 (fraud)"
            }), 400
        
        success = update_prediction_feedback(
            prediction_id,
            actual_class,
            feedback_note
        )
        
        if success:
            # Auto-trigger retraining check
            if auto_trigger_retraining:
                try:
                    auto_trigger_retraining()
                except Exception as e:
                    print(f"⚠️  Auto-trigger check failed: {e}")
            
            return jsonify({
                "status": "success",
                "message": "Feedback recorded successfully",
                "prediction_id": prediction_id
            })
        else:
            return jsonify({
                "status": "error",
                "message": "Failed to record feedback"
            }), 500
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Get basic statistics"""
    if not DB_ENABLED:
        return jsonify({
            "total_predictions": 0,
            "with_feedback": 0,
            "feedback_rate": 0,
            "by_model": {"banking": 0, "credit_card": 0}
        })
    
    try:
        # This would call database functions
        return jsonify({
            "total_predictions": 0,
            "with_feedback": 0,
            "feedback_rate": 0,
            "by_model": {"banking": 0, "credit_card": 0}
        })
    except Exception as e:
        return jsonify({
            "total_predictions": 0,
            "with_feedback": 0,
            "feedback_rate": 0,
            "by_model": {"banking": 0, "credit_card": 0}
        })

# ============================================
# SHUTDOWN HANDLER
# ============================================
@app.teardown_appcontext
def shutdown_session(exception=None):
    """Close database on shutdown"""
    if DB_ENABLED:
        try:
            close_database()
        except:
            pass

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    print("\n🚀 Starting Integrated Fraud Detection Server...")
    print(f"📍 Port: {port}\n")
    print("Modes:")
    print("  • banking: Raw transaction data")
    print("  • credit_card: V1-V28 + Amount + Time\n")
    app.run(host="0.0.0.0", port=port, debug=False)
