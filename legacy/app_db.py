
# #### 
# # app_db.py - Flask app WITH database integration AND auto-retraining
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import pandas as pd
# import json
# import joblib
# from xgboost import XGBClassifier
# import numpy as np
# from datetime import datetime
# import os
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# # Import database functions
# from database.db import (
#     init_database, 
#     close_database, 
#     save_prediction,
#     get_prediction_by_id,
#     get_recent_predictions,
#     update_prediction_feedback,
#     get_feedback_count
# )

# # Import analytics and retraining
# from analytics_routes import register_analytics_routes
# from retraining_routes import register_retraining_routes, check_and_trigger_retraining

# print("🚀 Fraud Detection API with Database Starting...")

# # Initialize Flask
# app = Flask(__name__)
# CORS(app)

# # Load model
# model = XGBClassifier()
# try:
#     model.load_model("models/fraud_model_final.json")
#     print("✅ Model loaded: fraud_model_final.json")
# except:
#     model.load_model("models/fraud_model_improved.json")
#     print("✅ Model loaded: fraud_model_improved.json")

# # Load scaler and features
# amount_scaler = joblib.load("models/amount_scaler.pkl")
# with open("models/features.json") as f:
#     FEATURES = json.load(f)

# print(f"✅ Model ready. Features: {len(FEATURES)}")

# # Load model config
# try:
#     with open("models/model_config.json") as f:
#         MODEL_CONFIG = json.load(f)
#     DEFAULT_THRESHOLD = MODEL_CONFIG.get("default_threshold", 0.4)
# except:
#     DEFAULT_THRESHOLD = 0.4

# print(f"✅ Default threshold: {DEFAULT_THRESHOLD}")

# # Initialize SHAP
# SHAP_ENABLED = False
# try:
#     from shap_explainer import SHAPExplainer
#     shap_explainer = SHAPExplainer(model, FEATURES)
#     SHAP_ENABLED = True
#     print("✅ SHAP explainer loaded")
# except Exception as e:
#     print(f"⚠️  SHAP not available: {e}")

# # Initialize GenAI
# GENAI_ENABLED = False
# genai_explain = None
# try:
#     from genai import explain_transaction
#     genai_explain = explain_transaction
#     GENAI_ENABLED = True
#     print("✅ GenAI loaded")
# except Exception as e:
#     print(f"⚠️  GenAI not available: {e}")

# # Initialize database
# DB_ENABLED = init_database()
# if DB_ENABLED:
#     print("✅ Database connected")
# else:
#     print("⚠️  Database not available - predictions won't be saved")

# # Import feature engineering
# from features.features_eng import engineer_features

# print("\n" + "="*60)
# print("✅ ALL SYSTEMS READY")
# print(f"✅ SHAP: {'ENABLED' if SHAP_ENABLED else 'DISABLED'}")
# print(f"✅ GenAI: {'ENABLED' if GENAI_ENABLED else 'DISABLED'}")
# print(f"✅ Database: {'ENABLED' if DB_ENABLED else 'DISABLED'}")
# print("="*60 + "\n")


# def prepare_features_for_prediction(data):
#     """Prepare features for prediction"""
#     df = pd.DataFrame([data])
#     df = engineer_features(df)
#     df["Amount"] = amount_scaler.transform(df[["Amount"]])
    
#     for col in FEATURES:
#         if col not in df.columns:
#             df[col] = 0
    
#     return df[FEATURES]


# def get_shap_explanations(X):
#     """Get SHAP explanations"""
#     if not SHAP_ENABLED:
#         return []
    
#     try:
#         explanations = shap_explainer.explain(X)
#         return explanations.get('detailed', [])[:5]
#     except Exception as e:
#         print(f"⚠️  SHAP explanation failed: {e}")
#         return []


# def get_genai_explanation(top_features, fraud_prob):
#     """Get GenAI explanation"""
#     if not GENAI_ENABLED or not genai_explain:
#         return None
    
#     try:
#         shap_features = [
#             (feat['feature'], feat['value'], feat['contribution'])
#             for feat in top_features[:5]
#         ]
#         explanation = genai_explain(shap_features, fraud_prob)
#         return explanation
#     except Exception as e:
#         print(f"⚠️  GenAI explanation failed: {e}")
#         return None


# def get_risk_level(fraud_prob):
#     """Get risk level based on probability"""
#     if fraud_prob >= 0.9:
#         return "CRITICAL"
#     elif fraud_prob >= 0.7:
#         return "HIGH"
#     elif fraud_prob >= 0.5:
#         return "MEDIUM"
#     elif fraud_prob >= 0.3:
#         return "LOW"
#     else:
#         return "MINIMAL"


# # ============================================
# # ROUTES
# # ============================================

# @app.route("/", methods=["GET"])
# def home():
#     """Health check"""
#     return jsonify({
#         "status": "healthy",
#         "service": "Fraud Detection API",
#         "version": "2.0 - With Database & Auto-Retraining",
#         "features": {
#             "shap": SHAP_ENABLED,
#             "genai": GENAI_ENABLED,
#             "database": DB_ENABLED
#         },
#         "endpoints": [
#             "POST /predict_explain - Make prediction with explanations",
#             "GET /api/predictions - Get recent predictions",
#             "GET /api/predictions/<id> - Get specific prediction",
#             "POST /api/predictions/<id>/feedback - Submit feedback"
#         ]
#     })


# @app.route("/predict_explain", methods=["POST"])
# def predict_explain():
#     """Make prediction with SHAP + GenAI explanation AND save to database"""
#     try:
#         data = request.get_json()
        
#         # Store original data for database
#         original_data = data.copy()
        
#         # Prepare features
#         X = prepare_features_for_prediction(data)
        
#         # Predict
#         proba = model.predict_proba(X)[0][1]
#         pred = int(proba >= DEFAULT_THRESHOLD)
        
#         # Get risk level
#         risk_level = get_risk_level(proba)
        
#         # Get SHAP explanations
#         top_features = get_shap_explanations(X)
        
#         # Get GenAI explanation
#         ai_explanation = get_genai_explanation(top_features, proba)
        
#         # Build response
#         response = {
#             "status": "success",
#             "prediction": pred,
#             "fraud_probability": float(proba),
#             "message": "⚠️ FRAUD DETECTED" if pred == 1 else "✅ Transaction Normal",
#             "risk_level": risk_level,
#             "threshold_used": DEFAULT_THRESHOLD,
#             "transaction_amount": float(data.get('Amount', 0)),
#             "top_contributing_features": top_features,
#             "ai_explanation": ai_explanation,
#             "ai_provider": "groq model" if GENAI_ENABLED else None
#         }
        
#         # Save to database
#         if DB_ENABLED:
#             try:
#                 db_data = {
#                     'transaction_time': original_data.get('Time', 0),
#                     'amount': original_data.get('Amount', 0),
#                     'prediction': pred,
#                     'fraud_probability': float(proba),
#                     'risk_level': risk_level,
#                     'threshold_used': DEFAULT_THRESHOLD,
#                     'top_features': top_features,
#                     'ai_explanation': ai_explanation,
#                     'ai_provider': 'groq' if GENAI_ENABLED else None,
#                     'api_endpoint': '/predict_explain',
#                     'request_ip': request.remote_addr
#                 }
                
#                 for i in range(1, 29):
#                     v_key = f'V{i}'
#                     db_data[v_key.lower()] = original_data.get(v_key, 0)
                
#                 prediction_id = save_prediction(db_data)
                
#                 if prediction_id:
#                     response['prediction_id'] = prediction_id
#                     print(f"✅ Prediction saved to database: ID {prediction_id}")
#                 else:
#                     print("⚠️  Failed to save prediction to database")
                    
#             except Exception as e:
#                 print(f"⚠️  Database save error: {e}")
        
#         return jsonify(response)
        
#     except Exception as e:
#         print(f"❌ Error: {e}")
#         return jsonify({
#             "status": "error",
#             "message": str(e)
#         }), 500


# @app.route("/api/predictions", methods=["GET"])
# def get_predictions():
#     """Get recent predictions from database"""
#     if not DB_ENABLED:
#         return jsonify({
#             "status": "error",
#             "message": "Database not available"
#         }), 503
    
#     try:
#         limit = request.args.get('limit', 50, type=int)
#         predictions = get_recent_predictions(limit)
        
#         return jsonify({
#             "status": "success",
#             "count": len(predictions),
#             "predictions": [dict(p) for p in predictions]
#         })
#     except Exception as e:
#         return jsonify({
#             "status": "error",
#             "message": str(e)
#         }), 500


# @app.route("/api/predictions/<int:prediction_id>", methods=["GET"])
# def get_prediction(prediction_id):
#     """Get specific prediction by ID"""
#     if not DB_ENABLED:
#         return jsonify({
#             "status": "error",
#             "message": "Database not available"
#         }), 503
    
#     try:
#         prediction = get_prediction_by_id(prediction_id)
        
#         if prediction:
#             return jsonify({
#                 "status": "success",
#                 "prediction": dict(prediction)
#             })
#         else:
#             return jsonify({
#                 "status": "error",
#                 "message": "Prediction not found"
#             }), 404
#     except Exception as e:
#         return jsonify({
#             "status": "error",
#             "message": str(e)
#         }), 500


# @app.route("/api/predictions/<int:prediction_id>/feedback", methods=["POST"])
# def submit_feedback(prediction_id):
#     """Submit feedback for a prediction"""
#     if not DB_ENABLED:
#         return jsonify({
#             "status": "error",
#             "message": "Database not available"
#         }), 503
    
#     try:
#         data = request.get_json()
#         actual_class = data.get('actual_class')
#         feedback_note = data.get('feedback_note', '')
        
#         if actual_class not in [0, 1]:
#             return jsonify({
#                 "status": "error",
#                 "message": "actual_class must be 0 (normal) or 1 (fraud)"
#             }), 400
        
#         success = update_prediction_feedback(
#             prediction_id,
#             actual_class,
#             feedback_note
#         )
        
#         if success:
#             # ============================================
#             # AUTO-TRIGGER RETRAINING CHECK
#             # ============================================
#             try:
#                 feedback_count = get_feedback_count()
#                 triggered = check_and_trigger_retraining(feedback_count)
                
#                 if triggered:
#                     print(f"🎯 Auto-retraining triggered at {feedback_count} feedbacks")
#             except Exception as e:
#                 print(f"⚠️  Auto-trigger check failed: {e}")
#             # ============================================
            
#             return jsonify({
#                 "status": "success",
#                 "message": "Feedback recorded successfully",
#                 "prediction_id": prediction_id
#             })
#         else:
#             return jsonify({
#                 "status": "error",
#                 "message": "Failed to record feedback"
#             }), 500
            
#     except Exception as e:
#         return jsonify({
#             "status": "error",
#             "message": str(e)
#         }), 500


# # ============================================
# # REGISTER ANALYTICS AND RETRAINING ROUTES
# # ============================================
# register_analytics_routes(app)
# register_retraining_routes(app)


# # ============================================
# # STARTUP & SHUTDOWN
# # ============================================

# @app.teardown_appcontext
# def shutdown_session(exception=None):
#     """Close database on shutdown"""
#     if DB_ENABLED:
#         close_database()


# if __name__ == "__main__":
#     print("\n🚀 Starting Flask server...")
#     print("📍 API will be available at: http://localhost:5000")
#     print("="*60 + "\n")
    
#     try:
#         app.run(host="0.0.0.0", port=5000, debug=True)
#     finally:
#         if DB_ENABLED:
#             close_database()
#             print("\n✅ Database connections closed")



#### updated app_db.py ######
# app_db.py - FIXED VERSION (Passes V1-V28 to database)
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import json
import joblib
from xgboost import XGBClassifier
import numpy as np
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# ============================================
# CONFIGURATION
# ============================================
DEFAULT_THRESHOLD = 0.4
DB_ENABLED = True

# ============================================
# LOAD MODEL AND DEPENDENCIES
# ============================================
print("\n🚀 Fraud Detection API with Database Starting...")
print("="*60)

# Load model
model = XGBClassifier()
try:
    model.load_model("models/fraud_model_final.json")
    print("✅ Model loaded: fraud_model_final.json")
except:
    model.load_model("models/fraud_model_improved.json")
    print("✅ Model loaded: fraud_model_improved.json")

# Load features list
with open("models/features.json") as f:
    FEATURES = json.load(f)
    print(f"✅ Model ready. Features: {len(FEATURES)}")
    print(f"✅ Default threshold: {DEFAULT_THRESHOLD}")

# Load scaler
amt_scaler = joblib.load("models/amount_scaler.pkl")

# Load SHAP explainer
try:
    from shap_explainer import ShapExplainer
    shap_explainer = ShapExplainer(model, FEATURES)
    print("✅ SHAP explainer loaded")
except Exception as e:
    print(f"⚠️  SHAP not available: {e}")
    shap_explainer = None

# Load GenAI
try:
    from genai import explain_transaction
    genai_explain = explain_transaction
    print("✅ GenAI loaded")
except Exception as e:
    print(f"⚠️  GenAI not available: {e}")
    genai_explain = None

# ============================================
# DATABASE SETUP
# ============================================
try:
    from database.db import (
        init_database,
        close_database,
        save_prediction,
        get_prediction_by_id,
        get_recent_predictions,
        update_prediction_feedback,
        get_feedback_count
    )
    
    init_database()
    print("✅ Database connected")
    DB_ENABLED = True
except Exception as e:
    print(f"⚠️  Database not available: {e}")
    DB_ENABLED = False

# ============================================
# IMPORT ANALYTICS AND RETRAINING ROUTES
# ============================================
try:
    from analytics_routes import register_analytics_routes
    from retraining_routes import register_retraining_routes, check_and_trigger_retraining
    
    register_analytics_routes(app)
    register_retraining_routes(app)
except Exception as e:
    print(f"⚠️  Routes registration failed: {e}")

print("="*60)
print("✅ ALL SYSTEMS READY")
print(f"✅ SHAP: {'ENABLED' if shap_explainer else 'DISABLED'}")
print(f"✅ GenAI: {'ENABLED' if genai_explain else 'DISABLED'}")
print(f"✅ Database: {'ENABLED' if DB_ENABLED else 'DISABLED'}")
print("="*60)

# ============================================
# FEATURE ENGINEERING
# ============================================
from features.features_eng import engineer_features

def prepare_features_for_prediction(data):
    """Prepare features for prediction"""
    df = pd.DataFrame([data])
    df = engineer_features(df)
    
    # Scale Amount
    if "Amount" in df.columns:
        df["Amount"] = amt_scaler.transform(df[["Amount"]])
    
    # Ensure all required features exist
    for col in FEATURES:
        if col not in df.columns:
            df[col] = 0
    
    return df[FEATURES]

# ============================================
# HELPER FUNCTIONS
# ============================================
def get_risk_level(probability, threshold):
    """Determine risk level based on probability"""
    if probability >= 0.8:
        return "CRITICAL"
    elif probability >= 0.6:
        return "HIGH"
    elif probability >= threshold:
        return "MEDIUM"
    elif probability >= 0.2:
        return "LOW"
    else:
        return "MINIMAL"

def get_genai_explanation(top_features, fraud_prob):
    """Get GenAI explanation"""
    if not genai_explain:
        return None
    
    try:
        shap_features = [
            (feat['feature'], feat['value'], feat['contribution'])
            for feat in top_features[:5]
        ]
        explanation = genai_explain(shap_features, fraud_prob)
        return explanation
    except Exception as e:
        print(f"⚠️  GenAI explanation failed: {e}")
        return None

# ============================================
# MAIN PREDICTION ENDPOINT
# ============================================
@app.route("/predict_explain", methods=["POST"])
def predict_explain():
    """
    Main prediction endpoint with SHAP and GenAI explanations
    ✅ FIXED: Now properly passes V1-V28 to database
    """
    try:
        # Get request data
        data = request.get_json()
        
        # ✅ IMPORTANT: Store original V1-V28 values
        original_v_features = {}
        for i in range(1, 29):
            v_key = f'V{i}'
            original_v_features[v_key] = data.get(v_key, 0.0)
        
        # Prepare features for prediction
        X = prepare_features_for_prediction(data)
        
        # Make prediction
        proba = model.predict_proba(X)[0][1]
        pred = int(proba >= DEFAULT_THRESHOLD)
        
        # Get risk level
        risk_level = get_risk_level(proba, DEFAULT_THRESHOLD)
        
        # Determine message
        if pred == 1:
            message = "⚠️ FRAUD DETECTED"
            recommendation = "FLAG - Suspicious activity detected"
        else:
            message = "✅ Transaction Normal"
            recommendation = "APPROVE - Transaction appears normal"
        
        # Get SHAP explanations
        top_features = []
        if shap_explainer:
            try:
                top_features = shap_explainer.get_top_features(X, n=5)
            except Exception as e:
                print(f"⚠️  SHAP explanation failed: {e}")
        
        # Get GenAI explanation
        ai_explanation = get_genai_explanation(top_features, proba)
        
        # ✅ CRITICAL FIX: Save to database with ALL V features
        prediction_id = None
        if DB_ENABLED:
            try:
                prediction_record = {
                    'transaction_time': data.get('Time', 0),
                    'amount': float(data.get('Amount', 0)),
                    # ✅ Include ALL original V1-V28 features
                    **original_v_features,
                    'prediction': pred,
                    'fraud_probability': float(proba),
                    'risk_level': risk_level,
                    'top_features': json.dumps(top_features) if top_features else '{}',
                    'ai_explanation': ai_explanation or '',
                    'threshold_used': DEFAULT_THRESHOLD
                }
                
                prediction_id = save_prediction(prediction_record)
            except Exception as e:
                print(f"❌ Error saving to database: {e}")
        
        # Build response
        response = {
            "status": "success",
            "prediction": pred,
            "fraud_probability": round(float(proba), 6),
            "message": message,
            "risk_level": risk_level,
            "recommendation": recommendation,
            "transaction_amount": float(data.get('Amount', 0)),
            "threshold_used": DEFAULT_THRESHOLD
        }
        
        if prediction_id:
            response["prediction_id"] = prediction_id
        
        if top_features:
            response["top_contributing_features"] = top_features
        
        if ai_explanation:
            response["ai_explanation"] = ai_explanation
            response["ai_provider"] = "Gemini/Groq"
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# ============================================
# DATABASE API ENDPOINTS
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
            # ✅ Check if should trigger auto-retraining
            try:
                feedback_count = get_feedback_count()
                triggered = check_and_trigger_retraining(feedback_count)
                
                if triggered:
                    print(f"🎯 Auto-retraining triggered at {feedback_count} feedbacks")
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

# ============================================
# HEALTH CHECK
# ============================================
@app.route("/", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "service": "Fraud Detection API",
        "status": "online",
        "model_features": len(FEATURES),
        "default_threshold": DEFAULT_THRESHOLD,
        "database": "connected" if DB_ENABLED else "disconnected",
        "shap": "enabled" if shap_explainer else "disabled",
        "genai": "enabled" if genai_explain else "disabled"
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

# ============================================
# START SERVER
# ============================================
if __name__ == "__main__":
    print("\n🚀 Starting Flask server...")
    print(f"📍 API will be available at: http://localhost:5000")
    print("="*60)
    app.run(debug=True, host="0.0.0.0", port=5000)