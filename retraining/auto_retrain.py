# retraining/auto_retrain.py - Automatic Model Retraining System
"""
Automatic retraining system for fraud detection model
Handles background training, model versioning, and deployment
"""

import pandas as pd
import numpy as np
import json
import joblib
from datetime import datetime
import os
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_auc_score
)
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler

from database.db import get_feedback_for_retraining, db
from features.features_eng import engineer_features

# ============================================
# RETRAINING CONFIGURATION
# ============================================

RETRAINING_CONFIG = {
    'min_feedback_samples': 20,          # Minimum feedback to trigger retraining
    'min_fraud_samples': 5,              # Minimum fraud samples required
    'min_normal_samples': 5,             # Minimum normal samples required
    'test_size': 0.2,                    # Test split ratio
    'smote_ratio': 0.3,                  # SMOTE sampling strategy
    'undersample_ratio': 0.6,            # UnderSampling ratio
    'improvement_threshold': 0.02,       # Minimum F1 improvement (2%)
    'models_dir': 'models',
    'backup_dir': 'models/backups'
}


# ============================================
# MODEL VERSIONING
# ============================================

def get_current_model_version():
    """Get current active model version from database"""
    try:
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT version, model_path, threshold, performance_metrics
                FROM model_versions
                WHERE is_active = TRUE
                LIMIT 1
            """)
            result = cursor.fetchone()
            
            if result:
                return {
                    'version': result['version'],
                    'model_path': result['model_path'],
                    'threshold': float(result['threshold']),
                    'performance_metrics': result['performance_metrics']
                }
            return None
    except Exception as e:
        print(f"❌ Error getting current model version: {e}")
        return None


def get_next_version_number():
    """Generate next version number"""
    try:
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT version FROM model_versions
                ORDER BY created_at DESC
                LIMIT 1
            """)
            result = cursor.fetchone()
            
            if result:
                version = result['version']
                # Extract number from version like "final_v1.0" or "v2"
                import re
                numbers = re.findall(r'\d+', version)
                if numbers:
                    last_num = int(numbers[-1])
                    return f"v{last_num + 1}"
            
            return "v2"  # First retrained version
    except Exception as e:
        print(f"⚠️ Error getting version number: {e}")
        return f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}"


def save_model_version(version, model_path, threshold, performance_metrics):
    """Save new model version to database"""
    try:
        with db.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO model_versions (
                    version, model_path, threshold, performance_metrics, is_active
                ) VALUES (%s, %s, %s, %s, FALSE)
                RETURNING id
            """, (version, model_path, threshold, json.dumps(performance_metrics)))
            
            version_id = cursor.fetchone()['id']
            print(f"✅ Saved model version: {version} (ID: {version_id})")
            return version_id
    except Exception as e:
        print(f"❌ Error saving model version: {e}")
        return None


def activate_model_version(version_id):
    """Activate a model version (deactivate others)"""
    try:
        with db.get_cursor() as cursor:
            # Deactivate all models
            cursor.execute("UPDATE model_versions SET is_active = FALSE")
            
            # Activate new model
            cursor.execute("""
                UPDATE model_versions 
                SET is_active = TRUE 
                WHERE id = %s
            """, (version_id,))
            
            print(f"✅ Activated model version ID: {version_id}")
            return True
    except Exception as e:
        print(f"❌ Error activating model: {e}")
        return False


# ============================================
# DATA PREPARATION
# ============================================

def prepare_retraining_data():
    """
    Prepare data for retraining by combining:
    1. Original training data
    2. New feedback data from production
    """
    print("\n📊 Preparing retraining data...")
    
    # Load original training data
    print("  Loading original training data...")
    try:
        original_data = pd.read_csv("data/creditcard.csv")
        print(f"  ✅ Original data: {len(original_data):,} samples")
    except Exception as e:
        print(f"  ❌ Error loading original data: {e}")
        return None, None
    
    # Get feedback data from database
    print("  Loading feedback data...")
    feedback_data = get_feedback_for_retraining()
    
    if not feedback_data:
        print("  ❌ No feedback data available")
        return None, None
    
    feedback_df = pd.DataFrame(feedback_data)
    print(f"  ✅ Feedback data: {len(feedback_df)} samples")
    
    # Rename 'Class' column if it's named differently (from database)
    # The database query returns it as 'class' (lowercase)
    if 'class' in feedback_df.columns:
        feedback_df = feedback_df.rename(columns={'class': 'Class'})
    
    # Check balance
    fraud_count = feedback_df['Class'].sum()
    normal_count = len(feedback_df) - fraud_count
    
    print(f"  Feedback distribution:")
    print(f"    Fraud: {fraud_count}")
    print(f"    Normal: {normal_count}")
    
    if fraud_count < RETRAINING_CONFIG['min_fraud_samples']:
        print(f"  ⚠️  Not enough fraud samples (need {RETRAINING_CONFIG['min_fraud_samples']})")
        return None, None
    
    if normal_count < RETRAINING_CONFIG['min_normal_samples']:
        print(f"  ⚠️  Not enough normal samples (need {RETRAINING_CONFIG['min_normal_samples']})")
        return None, None
    
    # Combine datasets
    print("  Combining datasets...")
    combined_data = pd.concat([original_data, feedback_df], ignore_index=True)
    print(f"  ✅ Combined data: {len(combined_data):,} samples")
    
    # Apply feature engineering
    print("  Engineering features...")
    combined_data = engineer_features(combined_data)
    
    # Split features and labels
    X = combined_data.drop('Class', axis=1)
    y = combined_data['Class']
    
    # Handle missing values (NaN) before training
    print("  Handling missing values...")
    if X.isnull().any().any():
        nan_cols = X.columns[X.isnull().any()].tolist()
        print(f"    Found NaN in columns: {nan_cols[:5]}...")  # Show first 5
        X = X.fillna(0)  # Fill NaN with 0
        print("    ✅ NaN values filled with 0")
    
    print(f"  ✅ Ready for training: {X.shape[0]:,} samples, {X.shape[1]} features")
    print(f"  Fraud rate: {y.mean()*100:.4f}%")
    
    return X, y


# ============================================
# MODEL TRAINING
# ============================================

def train_new_model(X, y):
    """Train new model with updated data"""
    print("\n🤖 Training new model...")
    
    # Scale Amount feature
    print("  Scaling features...")
    amt_scaler = StandardScaler()
    X["Amount"] = amt_scaler.fit_transform(X[["Amount"]])
    
    # Train-test split
    print("  Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=RETRAINING_CONFIG['test_size'],
        stratify=y,
        random_state=42
    )
    
    print(f"  Train: {len(X_train):,} samples")
    print(f"  Test: {len(X_test):,} samples")
    
    # Balance training data
    print("  Balancing training data (SMOTE + UnderSampling)...")
    
    smote = SMOTE(
        random_state=42,
        sampling_strategy=RETRAINING_CONFIG['smote_ratio']
    )
    X_train_smote, y_train_smote = smote.fit_resample(X_train, y_train)
    
    undersample = RandomUnderSampler(
        random_state=42,
        sampling_strategy=RETRAINING_CONFIG['undersample_ratio']
    )
    X_train_balanced, y_train_balanced = undersample.fit_resample(
        X_train_smote, y_train_smote
    )
    
    print(f"  Balanced: {len(X_train_balanced):,} samples ({y_train_balanced.mean()*100:.1f}% fraud)")
    
    # Train model
    print("  Training XGBoost...")
    model = XGBClassifier(
        n_estimators=600,
        max_depth=4,
        min_child_weight=8,
        learning_rate=0.015,
        gamma=0.4,
        reg_alpha=0.08,
        reg_lambda=0.8,
        subsample=0.75,
        colsample_bytree=0.75,
        colsample_bylevel=0.75,
        scale_pos_weight=2.5,
        eval_metric='aucpr',
        random_state=42,
        n_jobs=-1,
        use_label_encoder=False
    )
    
    model.fit(X_train_balanced, y_train_balanced, verbose=False)
    print("  ✅ Training complete!")
    
    # Evaluate on test set
    print("\n📊 Evaluating new model...")
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    # Test multiple thresholds
    best_threshold = 0.4
    best_f1 = 0
    
    for threshold in [0.3, 0.35, 0.4, 0.45, 0.5]:
        y_pred = (y_pred_proba >= threshold).astype(int)
        f1 = f1_score(y_test, y_pred)
        
        if f1 > best_f1:
            best_f1 = f1
            best_threshold = threshold
    
    # Final predictions with best threshold
    y_pred = (y_pred_proba >= best_threshold).astype(int)
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_pred_proba)
    cm = confusion_matrix(y_test, y_pred)
    
    performance = {
        'accuracy': float(accuracy),
        'precision': float(precision),
        'recall': float(recall),
        'f1_score': float(f1),
        'roc_auc': float(roc_auc),
        'best_threshold': float(best_threshold),
        'confusion_matrix': {
            'tn': int(cm[0][0]),
            'fp': int(cm[0][1]),
            'fn': int(cm[1][0]),
            'tp': int(cm[1][1])
        },
        'trained_on_samples': int(len(X_train_balanced)),
        'test_samples': int(len(X_test))
    }
    
    print(f"  Accuracy: {accuracy:.4f}")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall: {recall:.4f}")
    print(f"  F1 Score: {f1:.4f}")
    print(f"  ROC-AUC: {roc_auc:.4f}")
    print(f"  Best Threshold: {best_threshold}")
    
    return model, amt_scaler, X.columns.tolist(), performance, best_threshold


# ============================================
# MODEL DEPLOYMENT
# ============================================

def deploy_new_model(model, scaler, features, performance, threshold):
    """Deploy new model if better than current"""
    print("\n🚀 Deploying new model...")
    
    # Get current model performance
    current_version = get_current_model_version()
    
    if current_version:
        current_f1 = current_version['performance_metrics'].get('f1_score', 0)
        new_f1 = performance['f1_score']
        improvement = new_f1 - current_f1
        
        print(f"  Current model F1: {current_f1:.4f}")
        print(f"  New model F1: {new_f1:.4f}")
        print(f"  Improvement: {improvement:+.4f} ({improvement*100:+.2f}%)")
        
        if improvement < RETRAINING_CONFIG['improvement_threshold']:
            print(f"  ⚠️  Improvement below threshold ({RETRAINING_CONFIG['improvement_threshold']})")
            print("  ❌ Keeping current model")
            return False
    
    # Generate version number
    version = get_next_version_number()
    model_filename = f"fraud_model_{version}.json"
    model_path = os.path.join(RETRAINING_CONFIG['models_dir'], model_filename)
    
    # Create backup directory
    os.makedirs(RETRAINING_CONFIG['backup_dir'], exist_ok=True)
    
    # Backup current model if exists
    if current_version and os.path.exists(current_version['model_path']):
        backup_path = os.path.join(
            RETRAINING_CONFIG['backup_dir'],
            f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.path.basename(current_version['model_path'])}"
        )
        import shutil
        shutil.copy(current_version['model_path'], backup_path)
        print(f"  ✅ Backed up current model to: {backup_path}")
    
    # Save new model
    print(f"  Saving new model: {model_path}")
    model.save_model(model_path)
    
    # Save scaler
    scaler_path = os.path.join(RETRAINING_CONFIG['models_dir'], "amount_scaler.pkl")
    joblib.dump(scaler, scaler_path)
    
    # Save features
    features_path = os.path.join(RETRAINING_CONFIG['models_dir'], "features.json")
    with open(features_path, 'w') as f:
        json.dump(features, f, indent=2)
    
    # Save performance config
    config = {
        'model_version': version,
        'training_date': datetime.now().isoformat(),
        'default_threshold': threshold,
        'performance': performance,
        'retraining_config': RETRAINING_CONFIG
    }
    
    config_path = os.path.join(RETRAINING_CONFIG['models_dir'], "model_config.json")
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print("  ✅ Model files saved")
    
    # Save to database
    version_id = save_model_version(version, model_path, threshold, performance)
    
    if version_id:
        # Activate new model
        if activate_model_version(version_id):
            print(f"  ✅ New model {version} activated!")
            return True
    
    print("  ❌ Failed to activate new model")
    return False


# ============================================
# MAIN RETRAINING FUNCTION
# ============================================

def retrain_model():
    """
    Main retraining function
    Returns: (success, message, performance)
    """
    print("\n" + "="*70)
    print("🔄 AUTOMATIC MODEL RETRAINING STARTED")
    print("="*70)
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    try:
        # Step 1: Prepare data
        X, y = prepare_retraining_data()
        
        if X is None or y is None:
            return False, "Insufficient data for retraining", None
        
        # Step 2: Train new model
        model, scaler, features, performance, threshold = train_new_model(X, y)
        
        # Step 3: Deploy if better
        deployed = deploy_new_model(model, scaler, features, performance, threshold)
        
        if deployed:
            print("\n" + "="*70)
            print("✅ RETRAINING SUCCESSFUL - NEW MODEL DEPLOYED")
            print("="*70)
            return True, "New model trained and deployed successfully", performance
        else:
            print("\n" + "="*70)
            print("⚠️  RETRAINING COMPLETE - MODEL NOT DEPLOYED")
            print("="*70)
            return False, "New model not better than current model", performance
            
    except Exception as e:
        error_msg = f"Retraining failed: {str(e)}"
        print(f"\n❌ {error_msg}")
        print("="*70)
        return False, error_msg, None


# ============================================
# TESTING
# ============================================

if __name__ == "__main__":
    print("🧪 Testing retraining module...")
    
    from database.db import init_database
    init_database()
    
    # Check readiness
    from database.analytics import check_retraining_readiness
    status = check_retraining_readiness(20)
    
    print(f"\nRetraining readiness:")
    print(f"  Feedback count: {status['feedback_count']}")
    print(f"  Ready: {status['ready_for_retraining']}")
    print(f"  Recommendation: {status['recommendation']}")
    
    if status['ready_for_retraining']:
        print("\n🚀 Starting retraining...")
        success, message, performance = retrain_model()
        
        print(f"\nResult: {message}")
        if performance:
            print(f"Performance: {json.dumps(performance, indent=2)}")
    else:
        print("\n⏸️  Not ready for retraining yet")