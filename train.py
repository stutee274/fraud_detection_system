# train_proper.py - Properly trained fraud detection model
import pandas as pd
import json
import joblib
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    recall_score, precision_score, f1_score, 
    classification_report, confusion_matrix,
    precision_recall_curve, roc_auc_score, roc_curve
)
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from imblearn.pipeline import Pipeline as ImbPipeline
from features.features_eng import engineer_features

print("="*70)
print("PROPER FRAUD DETECTION MODEL TRAINING")
print("="*70)

# Load data
print("\n Loading data...")
df = pd.read_csv("data/creditcard.csv")
print(f"Dataset shape: {df.shape}")
print(f"Fraud cases: {df['Class'].sum()} ({df['Class'].mean()*100:.4f}%)")

# Feature engineering
print("\n Engineering features...")
df = engineer_features(df)

# Separate features and target
X = df.drop("Class", axis=1)
y = df["Class"]

print(f"Features: {X.shape[1]}")
print(f"Feature names: {X.columns.tolist()[:10]}...")

# Scale Amount
print("\n⚖️  Scaling Amount...")
amt_scaler = StandardScaler()
X["Amount"] = amt_scaler.fit_transform(X[["Amount"]])
print(f"Amount scaled - Mean: {amt_scaler.mean_[0]:.2f}, Std: {amt_scaler.scale_[0]:.2f}")

# Train-test split with stratification
print("\n Splitting data (80% train, 20% test)...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

print(f"Train: {X_train.shape[0]:,} samples ({y_train.sum():,} frauds, {y_train.mean()*100:.4f}%)")
print(f"Test: {X_test.shape[0]:,} samples ({y_test.sum():,} frauds, {y_test.mean()*100:.4f}%)")

# ============================================
# BETTER RESAMPLING STRATEGY
# ============================================

print("\n" + "="*70)
print(" BALANCED RESAMPLING (SMOTE + UnderSampling)")
print("="*70)

# Strategy: Combine SMOTE (oversample minority) with UnderSampling (undersample majority)
# This is better than pure SMOTE which creates too many synthetic samples

# Step 1: SMOTE to increase fraud cases (but not to 1:1)
smote = SMOTE(random_state=42, sampling_strategy=0.3, k_neighbors=3)
# This means: for every 3 normal transactions, have 1 fraud (instead of 1:1)

# Step 2: Random undersample majority class
undersample = RandomUnderSampler(random_state=42, sampling_strategy=0.7)
# This means: final ratio will be ~1:1.4 (fraud:normal)

# Combine both
X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)
print(f"After SMOTE: {X_train_balanced.shape[0]:,} samples ({y_train_balanced.mean()*100:.2f}% fraud)")

X_train_balanced, y_train_balanced = undersample.fit_resample(X_train_balanced, y_train_balanced)
print(f"After UnderSampling: {X_train_balanced.shape[0]:,} samples ({y_train_balanced.mean()*100:.2f}% fraud)")

# ============================================
# BETTER MODEL CONFIGURATION
# ============================================

print("\n" + "="*70)
print(" TRAINING XGBOOST WITH OPTIMIZED PARAMETERS")
print("="*70)

# These parameters are specifically tuned for fraud detection
model = XGBClassifier(
    # Model complexity
    n_estimators=500,           # More trees = better learning
    max_depth=3,                # Shallow trees = less overfitting
    min_child_weight=10,        # Conservative splits = fewer false positives
    
    # Learning rate
    learning_rate=0.01,         # Slow learning = better generalization
    
    # Regularization
    gamma=0.5,                  # Minimum loss reduction to split
    reg_alpha=0.1,              # L1 regularization
    reg_lambda=1.0,             # L2 regularization
    
    # Sampling
    subsample=0.7,              # Use 70% of samples per tree
    colsample_bytree=0.7,       # Use 70% of features per tree
    colsample_bylevel=0.7,      # Use 70% of features per level
    
    # Class imbalance
    scale_pos_weight=3,         # Give fraud class 3x more weight
    
    # Other
    eval_metric='aucpr',        # Optimize precision-recall AUC
    random_state=42,
    use_label_encoder=False,
    n_jobs=-1                   # Use all CPU cores
)

print("Training model...")
print("(This may take a few minutes...)")

model.fit(
    X_train_balanced, 
    y_train_balanced,
    verbose=False
)

print("✅ Training complete!")

# ============================================
# EVALUATION
# ============================================

print("\n" + "="*70)
print("📊 MODEL EVALUATION")
print("="*70)

# Predictions
y_pred_proba = model.predict_proba(X_test)[:, 1]
y_pred_default = (y_pred_proba >= 0.5).astype(int)

# Basic metrics
print("\n📈 Performance at default threshold (0.5):")
print(f"  Recall (Fraud Detection Rate): {recall_score(y_test, y_pred_default):.4f}")
print(f"  Precision (Accuracy of Fraud Alerts): {precision_score(y_test, y_pred_default):.4f}")
print(f"  F1 Score: {f1_score(y_test, y_pred_default):.4f}")
print(f"  ROC-AUC: {roc_auc_score(y_test, y_pred_proba):.4f}")

# Confusion matrix
cm = confusion_matrix(y_test, y_pred_default)
print(f"\n🎯 Confusion Matrix:")
print(f"  True Negatives:  {cm[0,0]:,} (Correctly identified normal)")
print(f"  False Positives: {cm[0,1]:,} (Normal flagged as fraud)")
print(f"  False Negatives: {cm[1,0]:,} (Missed fraud)")
print(f"  True Positives:  {cm[1,1]:,} (Correctly caught fraud)")

print(f"\n💰 Business Metrics:")
print(f"  Fraud Caught: {cm[1,1]}/{cm[1,1]+cm[1,0]} = {cm[1,1]/(cm[1,1]+cm[1,0])*100:.1f}%")
print(f"  False Alarm Rate: {cm[0,1]}/{cm[0,0]+cm[0,1]} = {cm[0,1]/(cm[0,0]+cm[0,1])*100:.4f}%")

# ============================================
# OPTIMAL THRESHOLD SEARCH
# ============================================

print("\n" + "="*70)
print("🎯 FINDING OPTIMAL THRESHOLD")
print("="*70)

precisions, recalls, thresholds = precision_recall_curve(y_test, y_pred_proba)

# Find multiple optimal thresholds for different use cases
print("\n📊 Threshold Analysis:")

thresholds_to_check = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
results = []

for threshold in thresholds_to_check:
    y_pred_temp = (y_pred_proba >= threshold).astype(int)
    recall = recall_score(y_test, y_pred_temp)
    precision = precision_score(y_test, y_pred_temp) if y_pred_temp.sum() > 0 else 0
    f1 = f1_score(y_test, y_pred_temp) if y_pred_temp.sum() > 0 else 0
    
    results.append({
        'threshold': threshold,
        'recall': recall,
        'precision': precision,
        'f1': f1
    })
    
    print(f"\n  Threshold {threshold:.1f}:")
    print(f"    Recall: {recall:.1%} | Precision: {precision:.1%} | F1: {f1:.4f}")

# Find best F1 score threshold
best_f1_idx = max(range(len(results)), key=lambda i: results[i]['f1'])
best_f1_threshold = results[best_f1_idx]['threshold']

# Find threshold with precision >= 50%
precision_50_results = [r for r in results if r['precision'] >= 0.5]
if precision_50_results:
    best_precision_threshold = max(precision_50_results, key=lambda r: r['recall'])['threshold']
else:
    best_precision_threshold = 0.7

# Find threshold with recall >= 80%
recall_80_results = [r for r in results if r['recall'] >= 0.8]
if recall_80_results:
    best_recall_threshold = min(recall_80_results, key=lambda r: r['threshold'])['threshold']
else:
    best_recall_threshold = 0.3

print(f"\n🎯 RECOMMENDED THRESHOLDS:")
print(f"  Best F1 Score: {best_f1_threshold:.2f}")
print(f"  Best Precision (≥50%): {best_precision_threshold:.2f}")
print(f"  Best Recall (≥80%): {best_recall_threshold:.2f}")

# ============================================
# DETAILED EVALUATION AT RECOMMENDED THRESHOLDS
# ============================================

print("\n" + "="*70)
print("📋 DETAILED PERFORMANCE AT RECOMMENDED THRESHOLDS")
print("="*70)

for name, threshold in [
    ("High Security (catch all fraud)", best_recall_threshold),
    ("Balanced (best F1)", best_f1_threshold),
    ("High Precision (minimize false alarms)", best_precision_threshold)
]:
    y_pred_temp = (y_pred_proba >= threshold).astype(int)
    cm_temp = confusion_matrix(y_test, y_pred_temp)
    
    recall = recall_score(y_test, y_pred_temp)
    precision = precision_score(y_test, y_pred_temp)
    f1 = f1_score(y_test, y_pred_temp)
    
    print(f"\n{name} (threshold={threshold:.2f}):")
    print(f"  Recall: {recall:.1%} | Precision: {precision:.1%} | F1: {f1:.4f}")
    print(f"  Fraud Caught: {cm_temp[1,1]}/{cm_temp[1,1]+cm_temp[1,0]}")
    print(f"  False Alarms: {cm_temp[0,1]:,}")
    print(f"  For every 100 alerts, {precision*100:.0f} are real fraud")

# ============================================
# FEATURE IMPORTANCE
# ============================================

print("\n" + "="*70)
print("🔍 TOP 15 MOST IMPORTANT FEATURES")
print("="*70)

feature_importance = pd.DataFrame({
    'feature': X.columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

print(feature_importance.head(15).to_string(index=False))

# ============================================
# SAVE MODEL
# ============================================

print("\n" + "="*70)
print("💾 SAVING MODEL")
print("="*70)

model.save_model("models/fraud_model_improved.json")
joblib.dump(amt_scaler, "models/amount_scaler.pkl")

with open("models/features.json", "w") as f:
    json.dump(X.columns.tolist(), f, indent=2)

config = {
    "model_version": "2.0_proper",
    "training_date": pd.Timestamp.now().isoformat(),
    "default_threshold": float(best_f1_threshold),
    "recommended_thresholds": {
        "high_security": float(best_recall_threshold),
        "balanced": float(best_f1_threshold),
        "high_precision": float(best_precision_threshold)
    },
    "performance": {
        "roc_auc": float(roc_auc_score(y_test, y_pred_proba)),
        "best_f1_score": float(results[best_f1_idx]['f1']),
        "recall_at_best_f1": float(results[best_f1_idx]['recall']),
        "precision_at_best_f1": float(results[best_f1_idx]['precision'])
    },
    "training_info": {
        "total_samples": int(len(df)),
        "fraud_samples": int(y.sum()),
        "fraud_rate": float(y.mean()),
        "features": int(X.shape[1])
    }
}

with open("models/model_config.json", "w") as f:
    json.dump(config, f, indent=2)

print(f"\n✅ Saved:")
print(f"  - models/fraud_model_improved.json")
print(f"  - models/amount_scaler.pkl")
print(f"  - models/features.json")
print(f"  - models/model_config.json")

print("\n" + "="*70)
print("✅ TRAINING COMPLETE!")
print("="*70)

print(f"\n🎯 NEXT STEPS:")
print(f"  1. Review the performance metrics above")
print(f"  2. Choose appropriate threshold for your use case:")
print(f"     - Banking/High-value: Use {best_recall_threshold:.2f} (high security)")
print(f"     - E-commerce: Use {best_f1_threshold:.2f} (balanced)")
print(f"     - Auto-block: Use {best_precision_threshold:.2f} (high precision)")
print(f"  3. Update your Flask app to use: models/fraud_model_proper.json")
print(f"  4. Test with: python test_simple.py")

print("\n" + "="*70)