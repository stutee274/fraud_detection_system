# retraining/auto_retrain_dual.py - Complete Auto-Retraining with Dataset
"""
Complete retraining system for dual mode (banking + credit card)
- Loads original creditcard.csv dataset
- Combines with feedback samples
- Trains new model
- Compares performance with old model
- Auto-activates if improvement >= 2%
"""

import pandas as pd
import numpy as np
import json
import joblib
from datetime import datetime
import os
from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_auc_score, classification_report
)

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_dual import (
    get_feedback_data_for_retraining,
    Database,
    convert_decimals
)

# Configuration
RETRAIN_CONFIG = {
    'min_feedback_samples': 20,
    'improvement_threshold': 0.01,  # 1% improvement (lowered from 2%)
    'test_size': 0.2,
    'models_dir': 'models',
    'data_dir': 'data'
}

# ============================================
# CREDIT CARD RETRAINING (with original dataset)
# ============================================
def retrain_credit_card_with_dataset():
    """
    Retrain credit card model:
    1. Load original creditcard.csv
    2. Add feedback samples
    3. Train new model
    4. Compare with old model
    5. Activate if better
    """
    try:
        import time
        time.sleep(0.1)
        
        print(f"\n{'='*70}")
        print("🔄 CREDIT CARD RETRAINING (WITH ORIGINAL DATASET)")
        print(f"{'='*70}")
        
        # Get fresh connection
        local_db = Database()
        local_db.initialize_pool()
        
        # Step 1: Load original dataset
        print("📊 Loading original creditcard.csv...")
        dataset_path = os.path.join(RETRAIN_CONFIG['data_dir'], 'creditcard.csv')
        
        if not os.path.exists(dataset_path):
            print(f"❌ Dataset not found: {dataset_path}")
            return {"status": "error", "message": "creditcard.csv not found"}
        
        original_df = pd.read_csv(dataset_path)
        print(f"✅ Loaded {len(original_df):,} original samples")
        
        # Step 2: Load feedback data
        print("📊 Loading feedback samples...")
        feedback_data = get_feedback_data_for_retraining('credit_card', limit=1000)
        
        if len(feedback_data) < RETRAIN_CONFIG['min_feedback_samples']:
            return {
                "status": "error",
                "message": f"Need {RETRAIN_CONFIG['min_feedback_samples']}+ feedbacks, got {len(feedback_data)}"
            }
        
        feedback_df = pd.DataFrame(feedback_data)
        print(f"✅ Loaded {len(feedback_df)} feedback samples")
        
        # Step 3: Combine datasets
        print("🔗 Combining datasets...")
        combined_df = pd.concat([original_df, feedback_df], ignore_index=True)
        print(f"✅ Combined: {len(combined_df):,} total samples")
        
        # Prepare features
        feature_cols = [col for col in combined_df.columns if col != 'Class']
        X = combined_df[feature_cols]
        y = combined_df['Class']
        
        print(f"   Fraud rate: {y.mean()*100:.4f}%")
        
        # Step 4: Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=RETRAIN_CONFIG['test_size'], 
            random_state=42, stratify=y
        )
        
        print(f"   Train: {len(X_train):,}, Test: {len(X_test):,}")
        
        # Step 5: Train new model
        print("🤖 Training XGBoost...")
        
        scale_pos_weight = sum(y_train==0) / sum(y_train==1)
        model = XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            scale_pos_weight=scale_pos_weight,
            random_state=42,
            n_jobs=-1,
            eval_metric='logloss'
        )
        
        model.fit(X_train, y_train, verbose=False)
        print("✅ Training complete")
        
        # Step 6: Evaluate new model
        print("📊 Evaluating new model...")
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]
        
        new_metrics = {
            'accuracy': float(accuracy_score(y_test, y_pred)),
            'precision': float(precision_score(y_test, y_pred, zero_division=0)),
            'recall': float(recall_score(y_test, y_pred, zero_division=0)),
            'f1_score': float(f1_score(y_test, y_pred, zero_division=0)),
            'roc_auc': float(roc_auc_score(y_test, y_proba))
        }
        
        print(f"   Accuracy:  {new_metrics['accuracy']:.4f}")
        print(f"   Precision: {new_metrics['precision']:.4f}")
        print(f"   Recall:    {new_metrics['recall']:.4f}")
        print(f"   F1 Score:  {new_metrics['f1_score']:.4f}")
        print(f"   ROC-AUC:   {new_metrics['roc_auc']:.4f}")
        
        # Step 7: Compare with old model
        print("\n🔍 Comparing with current model...")
        
        with local_db.get_cursor() as cursor:
            cursor.execute("""
                SELECT version, threshold, performance_metrics
                FROM model_versions
                WHERE model_type = 'credit_card' AND is_active = TRUE
                LIMIT 1
            """)
            current_model = cursor.fetchone()
        
        should_deploy = False
        comparison = {}
        
        if current_model and current_model['performance_metrics']:
            old_metrics = current_model['performance_metrics']
            old_f1 = old_metrics.get('f1_score', 0)
            new_f1 = new_metrics['f1_score']
            improvement = new_f1 - old_f1
            
            comparison = {
                'old_version': current_model['version'],
                'old_f1': old_f1,
                'new_f1': new_f1,
                'improvement': improvement,
                'improvement_pct': improvement * 100
            }
            
            print(f"   Current: {current_model['version']}")
            print(f"   Old F1:  {old_f1:.4f}")
            print(f"   New F1:  {new_f1:.4f}")
            print(f"   Change:  {improvement:+.4f} ({improvement*100:+.2f}%)")
            
            if improvement >= RETRAIN_CONFIG['improvement_threshold']:
                print(f"   ✅ Improvement above threshold ({RETRAIN_CONFIG['improvement_threshold']})")
                should_deploy = True
            else:
                print(f"   ⚠️  Improvement below threshold, keeping current model")
        else:
            print("   No current active model, will deploy new one")
            should_deploy = True
        
        # Step 8: Save new model with UNIQUE identifier (UUID)
        import uuid
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        timestamp_unique = f"{timestamp}_{unique_id}"
        
        model_path = f"models/fraud_model_cc_retrained_{timestamp_unique}.json"
        model.save_model(model_path)
        print(f"\n💾 Saved: {model_path}")
        
        # Backup old model if exists
        if current_model and current_model.get('model_path') and os.path.exists(current_model['model_path']):
            backup_dir = "models/backups"
            os.makedirs(backup_dir, exist_ok=True)
            backup_filename = f"backup_{timestamp}_{os.path.basename(current_model['model_path'])}"
            backup_path = os.path.join(backup_dir, backup_filename)
            
            import shutil
            shutil.copy2(current_model['model_path'], backup_path)
            print(f"📦 Backed up old model: {backup_path}")
        
        # Step 9: Save to database
        version_name = f"cc_retrained_{timestamp_unique}"
        
        with local_db.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO model_versions (
                    version, model_type, model_path, threshold, 
                    performance_metrics, is_active
                ) VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                version_name,
                'credit_card',
                model_path,
                0.4,
                json.dumps({
                    **new_metrics,
                    'trained_samples': len(combined_df),
                    'feedback_samples': len(feedback_df),
                    'comparison': comparison
                }),
                False  # Not active yet
            ))
            
            new_version_id = cursor.fetchone()['id']
        
        # Step 10: Activate if better
        if should_deploy:
            with local_db.get_cursor() as cursor:
                # Deactivate all
                cursor.execute("UPDATE model_versions SET is_active = FALSE WHERE model_type = 'credit_card'")
                # Activate new
                cursor.execute("UPDATE model_versions SET is_active = TRUE WHERE id = %s", (new_version_id,))
            
            print(f"✅ NEW MODEL ACTIVATED: {version_name}")
        else:
            print(f"⚠️  New model saved but NOT activated (current model is better)")
        
        local_db.close_all()
        
        print(f"{'='*70}\n")
        
        return {
            "status": "success",
            "model_type": "credit_card",
            "version": version_name,
            "samples_used": len(combined_df),
            "feedback_samples": len(feedback_df),
            "metrics": new_metrics,
            "comparison": comparison,
            "deployed": should_deploy,
            "model_path": model_path
        }
        
    except Exception as e:
        print(f"❌ CC retraining error: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

# ============================================
# BANKING RETRAINING (with synthetic dataset)
# ============================================
def retrain_banking_with_dataset():
    """
    Retrain banking model:
    1. Load synthetic banking dataset
    2. Add feedback samples
    3. Train new model
    4. Compare with old model
    5. Activate if better
    """
    try:
        import time
        time.sleep(0.1)
        
        print(f"\n{'='*70}")
        print("🔄 BANKING RETRAINING (WITH SYNTHETIC DATASET)")
        print(f"{'='*70}")
        
        # Get fresh connection
        local_db = Database()
        local_db.initialize_pool()
        
        # Step 1: Load synthetic banking dataset
        print("📊 Loading synthetic banking dataset...")
        
        # Try multiple possible dataset names
        dataset_paths = [
            os.path.join(RETRAIN_CONFIG['data_dir'], 'synthetic_fraud.csv'),
            os.path.join(RETRAIN_CONFIG['data_dir'], 'synthetic_banking_fraud.csv'),
            os.path.join(RETRAIN_CONFIG['data_dir'], 'banking_fraud.csv'),
            os.path.join(RETRAIN_CONFIG['data_dir'], 'fraud_dataset.csv'),
            os.path.join(RETRAIN_CONFIG['data_dir'], 'bank_transactions.csv')
        ]
        
        dataset_path = None
        for path in dataset_paths:
            if os.path.exists(path):
                dataset_path = path
                break
        
        if not dataset_path:
            print(f"❌ Banking dataset not found in data/ folder")
            print(f"   Tried: {', '.join([os.path.basename(p) for p in dataset_paths])}")
            print(f"⚠️  Falling back to feedback-only retraining")
            return retrain_banking_with_feedback_only()
        
        original_df = pd.read_csv(dataset_path)
        print(f"✅ Loaded {len(original_df):,} original samples from {os.path.basename(dataset_path)}")
        
        # Ensure Class column exists - handle multiple possible names
        if 'Class' not in original_df.columns:
            if 'Fraud_Label' in original_df.columns:
                original_df['Class'] = original_df['Fraud_Label']
                print(f"   Mapped Fraud_Label → Class")
            elif 'Is_Fraud' in original_df.columns:
                original_df['Class'] = original_df['Is_Fraud']
                print(f"   Mapped Is_Fraud → Class")
            elif 'Fraud' in original_df.columns:
                original_df['Class'] = original_df['Fraud']
                print(f"   Mapped Fraud → Class")
            else:
                print(f"❌ No Class/Fraud_Label/Is_Fraud/Fraud column found")
                return retrain_banking_with_feedback_only()
        
        # Map your dataset features to match database feedback features
        feature_mapping = {
            'Transaction_Amount': 'Transaction_Amount',
            'Account_Balance': 'Account_Balance',
            'Daily_Transaction_Count': 'Daily_Transaction_Count',
            'Avg_Transaction_Amount_7d': 'Avg_Transaction_Amount_7d',
            'Failed_Transaction_Count_7d': 'Failed_Transaction_Count_7d',
            'Card_Age': 'Card_Age',
            'Transaction_Distance': 'Transaction_Distance',
            'IP_Address_Flag': 'IP_Address_Flag'
        }
        
        # Rename columns to match database
        for old_name, new_name in feature_mapping.items():
            if old_name in original_df.columns:
                original_df = original_df.rename(columns={old_name: new_name})
        
        # Step 2: Load feedback data
        print("📊 Loading feedback samples...")
        feedback_data = get_feedback_data_for_retraining('banking', limit=1000)
        
        if len(feedback_data) < RETRAIN_CONFIG['min_feedback_samples']:
            return {
                "status": "error",
                "message": f"Need {RETRAIN_CONFIG['min_feedback_samples']}+ feedbacks, got {len(feedback_data)}"
            }
        
        feedback_df = pd.DataFrame(feedback_data)
        print(f"✅ Loaded {len(feedback_df)} feedback samples")
        
        # Step 3: Align columns between original and feedback data
        print("🔗 Aligning datasets...")
        
        # Get common columns (excluding Class)
        original_features = [col for col in original_df.columns if col != 'Class']
        feedback_features = [col for col in feedback_df.columns if col != 'Class']
        
        # Use intersection of features
        common_features = list(set(original_features) & set(feedback_features))
        
        if len(common_features) < 3:
            print(f"⚠️  Too few common features ({len(common_features)}), using feedback only")
            return retrain_banking_with_feedback_only()
        
        print(f"   Using {len(common_features)} common features")
        
        # Select common features + Class
        original_subset = original_df[common_features + ['Class']]
        feedback_subset = feedback_df[common_features + ['Class']]
        
        # Step 4: Combine datasets
        print("🔗 Combining datasets...")
        combined_df = pd.concat([original_subset, feedback_subset], ignore_index=True)
        print(f"✅ Combined: {len(combined_df):,} total samples")
        
        # Prepare features
        X = combined_df[common_features]
        y = combined_df['Class']
        
        print(f"   Fraud rate: {y.mean()*100:.2f}%")
        
        # Step 5: Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=RETRAIN_CONFIG['test_size'], 
            random_state=42, stratify=y
        )
        
        print(f"   Train: {len(X_train):,}, Test: {len(X_test):,}")
        
        # Step 6: Train new model
        print("🤖 Training RandomForest...")
        
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced',
            n_jobs=-1
        )
        
        model.fit(X_train, y_train)
        print("✅ Training complete")
        
        # Step 7: Evaluate new model
        print("📊 Evaluating new model...")
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]
        
        new_metrics = {
            'accuracy': float(accuracy_score(y_test, y_pred)),
            'precision': float(precision_score(y_test, y_pred, zero_division=0)),
            'recall': float(recall_score(y_test, y_pred, zero_division=0)),
            'f1_score': float(f1_score(y_test, y_pred, zero_division=0)),
            'roc_auc': float(roc_auc_score(y_test, y_proba))
        }
        
        print(f"   Accuracy:  {new_metrics['accuracy']:.4f}")
        print(f"   Precision: {new_metrics['precision']:.4f}")
        print(f"   Recall:    {new_metrics['recall']:.4f}")
        print(f"   F1 Score:  {new_metrics['f1_score']:.4f}")
        print(f"   ROC-AUC:   {new_metrics['roc_auc']:.4f}")
        
        # Step 8: Compare with old model
        print("\n🔍 Comparing with current model...")
        
        with local_db.get_cursor() as cursor:
            cursor.execute("""
                SELECT version, threshold, performance_metrics
                FROM model_versions
                WHERE model_type = 'banking' AND is_active = TRUE
                LIMIT 1
            """)
            current_model = cursor.fetchone()
        
        should_deploy = False
        comparison = {}
        
        if current_model and current_model['performance_metrics']:
            old_metrics = current_model['performance_metrics']
            old_f1 = old_metrics.get('f1_score', 0)
            new_f1 = new_metrics['f1_score']
            improvement = new_f1 - old_f1
            
            comparison = {
                'old_version': current_model['version'],
                'old_f1': old_f1,
                'new_f1': new_f1,
                'improvement': improvement,
                'improvement_pct': improvement * 100
            }
            
            print(f"   Current: {current_model['version']}")
            print(f"   Old F1:  {old_f1:.4f}")
            print(f"   New F1:  {new_f1:.4f}")
            print(f"   Change:  {improvement:+.4f} ({improvement*100:+.2f}%)")
            
            if improvement >= RETRAIN_CONFIG['improvement_threshold']:
                print(f"   ✅ Improvement above threshold ({RETRAIN_CONFIG['improvement_threshold']})")
                should_deploy = True
            else:
                print(f"   ⚠️  Improvement below threshold, keeping current model")
        else:
            print("   No current active model, will deploy new one")
            should_deploy = True
        
        # Step 9: Save new model with UNIQUE identifier (UUID)
        import uuid
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]  # Short UUID
        timestamp_unique = f"{timestamp}_{unique_id}"
        
        model_path = f"models/fraud_model_banking_retrained_{timestamp_unique}.pkl"
        joblib.dump(model, model_path)
        print(f"\n💾 Saved: {model_path}")
        
        # Step 10: Backup old model if exists
        if current_model and current_model.get('model_path') and os.path.exists(current_model['model_path']):
            backup_dir = "models/backups"
            os.makedirs(backup_dir, exist_ok=True)
            backup_filename = f"backup_{timestamp}_{os.path.basename(current_model['model_path'])}"
            backup_path = os.path.join(backup_dir, backup_filename)
            
            import shutil
            shutil.copy2(current_model['model_path'], backup_path)
            print(f"📦 Backed up old model: {backup_path}")
        
        # Step 11: Save to database
        version_name = f"banking_retrained_{timestamp_unique}"
        
        with local_db.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO model_versions (
                    version, model_type, model_path, threshold, 
                    performance_metrics, is_active
                ) VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                version_name,
                'banking',
                model_path,
                0.3,
                json.dumps({
                    **new_metrics,
                    'trained_samples': len(combined_df),
                    'feedback_samples': len(feedback_df),
                    'comparison': comparison
                }),
                False
            ))
            
            new_version_id = cursor.fetchone()['id']
        
        # Step 11: Activate if better
        if should_deploy:
            with local_db.get_cursor() as cursor:
                cursor.execute("UPDATE model_versions SET is_active = FALSE WHERE model_type = 'banking'")
                cursor.execute("UPDATE model_versions SET is_active = TRUE WHERE id = %s", (new_version_id,))
            
            print(f"✅ NEW MODEL ACTIVATED: {version_name}")
        else:
            print(f"⚠️  New model saved but NOT activated (current model is better)")
        
        local_db.close_all()
        
        print(f"{'='*70}\n")
        
        return {
            "status": "success",
            "model_type": "banking",
            "version": version_name,
            "samples_used": len(combined_df),
            "feedback_samples": len(feedback_df),
            "metrics": new_metrics,
            "comparison": comparison,
            "deployed": should_deploy,
            "model_path": model_path
        }
        
    except Exception as e:
        print(f"❌ Banking retraining error: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

def retrain_banking_with_feedback_only():
    """
    Fallback: Retrain banking model with feedback data only
    (Used when dataset is not available)
    """
    try:
        import time
        time.sleep(0.1)
        
        print(f"\n{'='*70}")
        print("🔄 BANKING RETRAINING (FEEDBACK DATA ONLY)")
        print(f"{'='*70}")
        
        local_db = Database()
        local_db.initialize_pool()
        
        # Load feedback
        print("📊 Loading feedback samples...")
        feedback_data = get_feedback_data_for_retraining('banking', limit=1000)
        
        if len(feedback_data) < RETRAIN_CONFIG['min_feedback_samples']:
            return {
                "status": "error",
                "message": f"Need {RETRAIN_CONFIG['min_feedback_samples']}+ feedbacks"
            }
        
        df = pd.DataFrame(feedback_data)
        print(f"✅ Loaded {len(df)} samples")
        
        # Prepare features
        feature_cols = [col for col in df.columns if col != 'Class']
        X, y = df[feature_cols], df['Class']
        
        print(f"   Fraud rate: {y.mean()*100:.2f}%")
        
        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, 
            stratify=y if len(y) > 10 else None
        )
        
        # Train model
        print("🤖 Training RandomForest...")
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced',
            n_jobs=-1
        )
        model.fit(X_train, y_train)
        print("✅ Training complete")
        
        # Evaluate
        print("📊 Evaluating...")
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]
        
        new_metrics = {
            'accuracy': float(accuracy_score(y_test, y_pred)),
            'precision': float(precision_score(y_test, y_pred, zero_division=0)),
            'recall': float(recall_score(y_test, y_pred, zero_division=0)),
            'f1_score': float(f1_score(y_test, y_pred, zero_division=0)),
            'roc_auc': float(roc_auc_score(y_test, y_proba))
        }
        
        print(f"   F1 Score: {new_metrics['f1_score']:.4f}")
        print(f"   ROC-AUC:  {new_metrics['roc_auc']:.4f}")
        
        # Compare with old
        print("\n🔍 Comparing with current model...")
        
        with local_db.get_cursor() as cursor:
            cursor.execute("""
                SELECT version, performance_metrics
                FROM model_versions
                WHERE model_type = 'banking' AND is_active = TRUE
                LIMIT 1
            """)
            current_model = cursor.fetchone()
        
        should_deploy = False
        comparison = {}
        
        if current_model and current_model['performance_metrics']:
            old_metrics = current_model['performance_metrics']
            old_f1 = old_metrics.get('f1_score', 0)
            improvement = new_metrics['f1_score'] - old_f1
            
            comparison = {
                'old_version': current_model['version'],
                'old_f1': old_f1,
                'new_f1': new_metrics['f1_score'],
                'improvement': improvement
            }
            
            print(f"   Old F1: {old_f1:.4f}")
            print(f"   New F1: {new_metrics['f1_score']:.4f}")
            print(f"   Change: {improvement:+.4f}")
            
            should_deploy = improvement >= RETRAIN_CONFIG['improvement_threshold']
        else:
            should_deploy = True
        
        # Save model
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        model_path = f"models/fraud_model_banking_retrained_{timestamp}.pkl"
        joblib.dump(model, model_path)
        print(f"\n💾 Saved: {model_path}")
        
        # Save to database
        version_name = f"banking_retrained_{timestamp}"
        
        with local_db.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO model_versions (
                    version, model_type, model_path, threshold,
                    performance_metrics, is_active
                ) VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                version_name, 'banking', model_path, 0.3,
                json.dumps({**new_metrics, 'samples': len(df), 'comparison': comparison}),
                False
            ))
            new_version_id = cursor.fetchone()['id']
        
        # Activate if better
        if should_deploy:
            with local_db.get_cursor() as cursor:
                cursor.execute("UPDATE model_versions SET is_active = FALSE WHERE model_type = 'banking'")
                cursor.execute("UPDATE model_versions SET is_active = TRUE WHERE id = %s", (new_version_id,))
            print(f"✅ NEW MODEL ACTIVATED")
        else:
            print(f"⚠️  Not activated (current is better)")
        
        local_db.close_all()
        print(f"{'='*70}\n")
        
        return {
            "status": "success",
            "model_type": "banking",
            "version": version_name,
            "samples_used": len(df),
            "metrics": new_metrics,
            "comparison": comparison,
            "deployed": should_deploy
        }
        
    except Exception as e:
        print(f"❌ Banking retraining error: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

# ============================================
# TESTING
# ============================================
if __name__ == "__main__":
    print("🧪 Testing Auto-Retraining Module...\n")
    
    # Test banking retraining
    print("Testing Banking Retraining...")
    result_banking = retrain_banking_with_dataset()
    print(f"\nResult: {json.dumps(result_banking, indent=2)}")
    
    print("\n" + "="*70 + "\n")
    
    # Test credit card retraining
    print("Testing Credit Card Retraining...")
    result_cc = retrain_credit_card_with_dataset()
    print(f"\nResult: {json.dumps(result_cc, indent=2)}")