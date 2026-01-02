# train_final.py - Final optimized training for production
import pandas as pd
import json
import joblib
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    recall_score, precision_score, f1_score, 
    classification_report, confusion_matrix,
    precision_recall_curve, roc_auc_score
)
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from features.features_eng import engineer_features

print("="*70)
print("🎯 FINAL PRODUCTION MODEL TRAINING")
print("="*70)

# ============================================
# 1. LOAD AND PREPARE DATA
# ============================================
print("\n📂 Step 1: Loading data...")
df = pd.read_csv("data/creditcard.csv")
print(f"Dataset shape: {df.shape}")
print(f"Fraud cases: {df['Class'].sum()} ({df['Class'].mean()*100:.4f}%)")

# ============================================
# 2. FEATURE ENGINEERING
# ============================================
print("\n🔧 Step 2: Engineering features...")
df = engineer_features(df)

X = df.drop("Class", axis=1)
y = df["Class"]

print(f"Features: {X.shape[1]}")
print(f"Feature list: {X.columns.tolist()}")

# ============================================
# 3. FEATURE SCALING
# ============================================
print("\n⚖️  Step 3: Scaling Amount feature...")
amt_scaler = StandardScaler()
X["Amount"] = amt_scaler.fit_transform(X[["Amount"]])
print(f"Amount scaled - Mean: {amt_scaler.mean_[0]:.2f}, Std: {amt_scaler.scale_[0]:.2f}")

# ============================================
# 4. TRAIN-TEST SPLIT
# ============================================
print("\n📊 Step 4: Splitting data...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, 
    test_size=0.2, 
    stratify=y, 
    random_state=42
)

print(f"Train: {X_train.shape[0]:,} samples ({y_train.sum()} frauds)")
print(f"Test: {X_test.shape[0]:,} samples ({y_test.sum()} frauds)")

# ============================================
# 5. BALANCED RESAMPLING
# ============================================
print("\n Step 5: Balanced resampling (SMOTE + UnderSampling)...")

# First: SMOTE to create synthetic fraud samples
smote = SMOTE(
    random_state=42, 
    sampling_strategy=0.3,  # For every 3 normals, create 1 fraud
    k_neighbors=5
)

X_train_smote, y_train_smote = smote.fit_resample(X_train, y_train)
print(f"After SMOTE: {X_train_smote.shape[0]:,} samples ({y_train_smote.mean()*100:.2f}% fraud)")

# Second: UnderSample to reduce normal class
undersample = RandomUnderSampler(
    random_state=42,
    sampling_strategy=0.6  # Final ratio: 3 normals for every 2 frauds
)

X_train_balanced, y_train_balanced = undersample.fit_resample(X_train_smote, y_train_smote)
print(f"After UnderSampling: {X_train_balanced.shape[0]:,} samples ({y_train_balanced.mean()*100:.2f}% fraud)")

# ============================================
# 6. MODEL TRAINING
# ============================================
print("\n🤖 Step 6: Training XGBoost model...")
print("This will take 2-5 minutes...")

model = XGBClassifier(
    # Tree structure
    n_estimators=600,           # More trees for better learning
    max_depth=4,                # Slightly deeper for complex patterns
    min_child_weight=8,         # Balance between overfitting and learning
    
    # Learning rate
    learning_rate=0.015,        # Slower learning for stability
    
    # Regularization (prevent overfitting)
    gamma=0.4,                  # Minimum loss reduction for split
    reg_alpha=0.08,             # L1 regularization
    reg_lambda=0.8,             # L2 regularization
    
    # Sampling (add randomness)
    subsample=0.75,             # Use 75% of samples per tree
    colsample_bytree=0.75,      # Use 75% of features per tree
    colsample_bylevel=0.75,     # Use 75% of features per level
    
    # Class imbalance handling
    scale_pos_weight=2.5,       # Weight fraud class 2.5x
    
    # Performance
    eval_metric='aucpr',        # Optimize precision-recall curve
    random_state=42,
    n_jobs=-1,                  # Use all CPU cores
    use_label_encoder=False
)

# Train
model.fit(
    X_train_balanced, 
    y_train_balanced,
    verbose=False
)

print("✅ Training complete!")

# ============================================
# 7. EVALUATION
# ============================================
print("\n📊 Step 7: Evaluating model...")

y_pred_proba = model.predict_proba(X_test)[:, 1]

# Test multiple thresholds
thresholds_to_test = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
results = []

print("\n📈 Performance at different thresholds:")
for threshold in thresholds_to_test:
    y_pred = (y_pred_proba >= threshold).astype(int)
    
    recall = recall_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred) if y_pred.sum() > 0 else 0
    f1 = f1_score(y_test, y_pred) if y_pred.sum() > 0 else 0
    
    results.append({
        'threshold': threshold,
        'recall': recall,
        'precision': precision,
        'f1': f1
    })
    
    cm = confusion_matrix(y_test, y_pred)
    fraud_caught = cm[1,1]
    total_fraud = cm[1,0] + cm[1,1]
    false_alarms = cm[0,1]
    
    print(f"\n  Threshold {threshold:.1f}:")
    print(f"    Recall: {recall:.1%} | Precision: {precision:.1%} | F1: {f1:.4f}")
    print(f"    Caught {fraud_caught}/{total_fraud} frauds | {false_alarms:,} false alarms")

# Find optimal thresholds
best_f1 = max(results, key=lambda x: x['f1'])
best_precision_50 = [r for r in results if r['precision'] >= 0.5]
best_precision = max(best_precision_50, key=lambda x: x['recall']) if best_precision_50 else results[-1]

print(f"\n🎯 RECOMMENDED THRESHOLDS:")
print(f"  Best F1: {best_f1['threshold']:.2f} (F1={best_f1['f1']:.4f})")
print(f"  Best Precision (≥50%): {best_precision['threshold']:.2f}")
print(f"  High Security: 0.3 (catch most fraud)")

# ============================================
# 8. FEATURE IMPORTANCE
# ============================================
print("\n🔍 Step 8: Feature importance analysis...")

feature_importance = pd.DataFrame({
    'feature': X.columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

print("\nTop 10 Most Important Features:")
print(feature_importance.head(10).to_string(index=False))

# Check if amount features dominate
amount_features = ['Amount', 'Amount_log', 'amount_roll_mean_3', 'amount_roll_std_3']
amount_importance = feature_importance[
    feature_importance['feature'].isin(amount_features)
]['importance'].sum()

print(f"\nAmount-related features: {amount_importance*100:.1f}% total importance")

if amount_importance > 0.4:
    print("⚠️  WARNING: Amount features dominate (>40%)")
    print("   Model may rely too heavily on transaction size")
else:
    print("✅ Good balance between amount and V features")

# ============================================
# 9. SAVE MODEL
# ============================================
print("\n💾 Step 9: Saving model...")

model.save_model("models/fraud_model_final.json")
joblib.dump(amt_scaler, "models/amount_scaler.pkl")

with open("models/features.json", "w") as f:
    json.dump(X.columns.tolist(), f, indent=2)

# Save comprehensive config
config = {
    "model_version": "final_v1.0",
    "training_date": pd.Timestamp.now().isoformat(),
    "default_threshold": float(best_f1['threshold']),
    "recommended_thresholds": {
        "high_security": 0.3,
        "balanced": float(best_f1['threshold']),
        "high_precision": float(best_precision['threshold'])
    },
    "performance": {
        "roc_auc": float(roc_auc_score(y_test, y_pred_proba)),
        "best_f1_score": float(best_f1['f1']),
        "recall_at_best_f1": float(best_f1['recall']),
        "precision_at_best_f1": float(best_f1['precision'])
    },
    "feature_importance": {
        "top_feature": feature_importance.iloc[0]['feature'],
        "top_importance": float(feature_importance.iloc[0]['importance']),
        "amount_features_total": float(amount_importance)
    },
    "training_info": {
        "total_samples": int(len(df)),
        "fraud_samples": int(y.sum()),
        "fraud_rate": float(y.mean()),
        "features_count": int(X.shape[1]),
        "smote_ratio": 0.3,
        "undersample_ratio": 0.6
    }
}

with open("models/model_config.json", "w") as f:
    json.dump(config, f, indent=2)

print(f"\n✅ Saved:")
print(f"  - models/fraud_model_final.json")
print(f"  - models/amount_scaler.pkl")
print(f"  - models/features.json")
print(f"  - models/model_config.json")

# ============================================
# 10. FINAL SUMMARY
# ============================================
print("\n" + "="*70)
print("✅ TRAINING COMPLETE!")
print("="*70)

print(f"\n📊 Model Performance Summary:")
print(f"  ROC-AUC: {roc_auc_score(y_test, y_pred_proba):.4f}")
print(f"  Best F1 Score: {best_f1['f1']:.4f} (at threshold {best_f1['threshold']:.2f})")
print(f"  Recommended Threshold: {best_f1['threshold']:.2f}")

print(f"\n🎯 Next Steps:")
print(f"  1. Update app_complete_gemini.py to load 'fraud_model_final.json'")
print(f"  2. Restart Flask: python app_complete_gemini.py")
print(f"  3. Test with real fraud samples: python test_real_fraud_samples.py")

print("\n" + "="*70)