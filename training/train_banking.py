# train_banking_fixed.py - FIXED FOR YOUR DATASET
"""
Improved banking fraud model with reduced false positives
Works with synthetic_fraud.csv (uses Fraud_Label not Is_Fraud)
"""

import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.preprocessing import StandardScaler
import joblib
import json
import os
from datetime import datetime

print("="*80)
print("🎯 IMPROVED BANKING FRAUD MODEL TRAINING")
print("="*80)

# ============================================
# LOAD DATA
# ============================================
print("\n📊 Loading training data...")

try:
    df = pd.read_csv('data/synthetic_fraud.csv')  # Changed filename
    print(f"✅ Loaded {len(df)} transactions")
    
    # Use correct column name
    y_column = 'Fraud_Label'  # Not 'Is_Fraud'
    
    print(f"   Fraud cases: {df[y_column].sum()} ({df[y_column].mean()*100:.2f}%)")
    print(f"   Normal cases: {(1-df[y_column]).sum()} ({(1-df[y_column]).mean()*100:.2f}%)")
except Exception as e:
    print(f"❌ Error loading data: {e}")
    exit(1)

# ============================================
# FEATURE ENGINEERING
# ============================================
print("\n🔧 Engineering features...")

# Time features
df['Timestamp'] = pd.to_datetime(df['Timestamp'])
df['hour'] = df['Timestamp'].dt.hour
df['day_of_week'] = df['Timestamp'].dt.dayofweek
df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)

# Amount features
df['amount'] = df['Transaction_Amount'].astype(float)
df['balance'] = df['Account_Balance'].astype(float)
df['spend_ratio'] = df['amount'] / (df['balance'] + df['amount'] + 1)

# Historical comparison (LESS SENSITIVE)
df['avg_7d'] = df['Avg_Transaction_Amount_7d'].astype(float)
df['amount_vs_avg'] = df['amount'] / (df['avg_7d'] + 1)
df['within_2x_avg'] = (df['amount'] <= df['avg_7d'] * 2).astype(int)
df['within_3x_avg'] = (df['amount'] <= df['avg_7d'] * 3).astype(int)

# Log transforms
df['amount_log'] = np.log1p(df['amount'])
df['balance_log'] = np.log1p(df['balance'])

# Time patterns (REFINED)
df['late_night'] = ((df['hour'] >= 23) | (df['hour'] <= 5)).astype(int)
df['very_late_night'] = ((df['hour'] >= 1) & (df['hour'] <= 4)).astype(int)
df['business_hours'] = ((df['hour'] >= 9) & (df['hour'] <= 17)).astype(int)

# Transaction type
df['is_atm'] = df['Transaction_Type'].str.contains('ATM', case=False, na=False).astype(int)
df['is_online'] = df['Transaction_Type'].str.contains('Online', case=False, na=False).astype(int)
df['is_pos'] = df['Transaction_Type'].str.contains('POS', case=False, na=False).astype(int)
df['is_transfer'] = df['Transaction_Type'].str.contains('Transfer', case=False, na=False).astype(int)

# Activity (LESS AGGRESSIVE)
df['daily_count'] = df['Daily_Transaction_Count'].astype(int)
df['very_high_daily_count'] = (df['daily_count'] > 15).astype(int)
df['reasonable_daily_count'] = (df['daily_count'] <= 10).astype(int)

# Failed transactions (MORE LENIENT)
df['failed_7d'] = df['Failed_Transaction_Count_7d'].astype(int)
df['few_failed'] = (df['failed_7d'] <= 2).astype(int)  # Trust indicator
df['many_failed'] = (df['failed_7d'] > 5).astype(int)  # Was 2

# Card age (REFINED)
df['card_age'] = df['Card_Age'].astype(int)
df['very_new_card'] = (df['card_age'] < 7).astype(int)
df['new_card'] = (df['card_age'] < 30).astype(int)
df['established_card'] = (df['card_age'] > 90).astype(int)  # Trust
df['mature_card'] = (df['card_age'] > 180).astype(int)

# Distance (REFINED)
df['distance'] = df['Transaction_Distance'].astype(float)
df['local_txn'] = (df['distance'] < 50).astype(int)
df['nearby_txn'] = (df['distance'] < 200).astype(int)
df['far_txn'] = (df['distance'] > 1000).astype(int)
df['very_far_txn'] = (df['distance'] > 3000).astype(int)

# Amount categories
df['small_amount'] = (df['amount'] < 100).astype(int)
df['normal_amount'] = ((df['amount'] >= 100) & (df['amount'] <= 500)).astype(int)
df['large_amount'] = (df['amount'] > 500).astype(int)
df['very_large_amount'] = (df['amount'] > 2000).astype(int)

# Balance categories
df['healthy_balance'] = (df['balance'] > 5000).astype(int)
df['low_balance'] = (df['balance'] < 1000).astype(int)

# Risk indicators
df['suspicious_ip'] = df['IP_Address_Flag'].astype(int)

# Trust score (NEW - reduces false positives)
df['trust_score'] = (
    df['established_card'] +
    df['few_failed'] +
    (df['balance'] >= df['amount']).astype(int) +
    df['within_2x_avg'] +
    df['reasonable_daily_count']
)

df['high_trust'] = (df['trust_score'] >= 4).astype(int)

print("✅ Feature engineering complete")

# ============================================
# SELECT FEATURES
# ============================================
feature_columns = [
    'amount', 'balance', 'spend_ratio', 'amount_vs_avg',
    'within_2x_avg', 'within_3x_avg',
    'amount_log', 'balance_log',
    'hour', 'day_of_week', 'is_weekend',
    'late_night', 'very_late_night', 'business_hours',
    'is_atm', 'is_online', 'is_pos', 'is_transfer',
    'daily_count', 'very_high_daily_count', 'reasonable_daily_count',
    'avg_7d', 'failed_7d', 'few_failed', 'many_failed',
    'card_age', 'very_new_card', 'new_card', 'established_card', 'mature_card',
    'distance', 'local_txn', 'nearby_txn', 'far_txn', 'very_far_txn',
    'small_amount', 'normal_amount', 'large_amount', 'very_large_amount',
    'healthy_balance', 'low_balance',
    'suspicious_ip',
    'trust_score', 'high_trust'
]

print(f"\n📋 Selected {len(feature_columns)} features")

X = df[feature_columns]
y = df[y_column]

# ============================================
# SPLIT DATA
# ============================================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\n📊 Data split:")
print(f"   Training: {len(X_train)} samples")
print(f"   Testing: {len(X_test)} samples")

# ============================================
# SCALE FEATURES
# ============================================
print("\n🔧 Scaling features...")

continuous_features = [
    'amount', 'balance', 'spend_ratio', 'amount_vs_avg',
    'amount_log', 'balance_log', 'hour', 'day_of_week',
    'daily_count', 'avg_7d', 'failed_7d', 'card_age', 'distance', 'trust_score'
]

scaler = StandardScaler()
X_train_scaled = X_train.copy()
X_test_scaled = X_test.copy()

X_train_scaled[continuous_features] = scaler.fit_transform(X_train[continuous_features])
X_test_scaled[continuous_features] = scaler.transform(X_test[continuous_features])

print("✅ Scaling complete")

# ============================================
# TRAIN MODEL
# ============================================
print("\n🎯 Training XGBoost model...")
print("   Optimized to reduce false positives")

model = XGBClassifier(
    max_depth=4,
    learning_rate=0.05,
    n_estimators=200,
    scale_pos_weight=3,  # Less aggressive
    min_child_weight=5,
    gamma=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    eval_metric='auc',
    use_label_encoder=False
)

print("\n⏳ Training...")
model.fit(X_train_scaled, y_train)
print("✅ Training complete!")

# ============================================
# EVALUATE
# ============================================
print("\n📊 Evaluating...")

y_pred = model.predict(X_test_scaled)
y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]

print("\n" + "="*60)
print("CLASSIFICATION REPORT")
print("="*60)
print(classification_report(y_test, y_pred, target_names=['Normal', 'Fraud']))

print("\nCONFUSION MATRIX")
print("="*60)
cm = confusion_matrix(y_test, y_pred)
print(f"True Negatives:  {cm[0][0]:>6}  (Correct Normal)")
print(f"False Positives: {cm[0][1]:>6}  (False Alarm)")
print(f"False Negatives: {cm[1][0]:>6}  (Missed Fraud)")
print(f"True Positives:  {cm[1][1]:>6}  (Caught Fraud)")

false_positive_rate = cm[0][1] / (cm[0][0] + cm[0][1])
print(f"\n📉 False Positive Rate: {false_positive_rate*100:.2f}%")

auc = roc_auc_score(y_test, y_pred_proba)
print(f"📈 ROC AUC Score: {auc:.4f}")

# ============================================
# SAVE MODEL
# ============================================
print("\n💾 Saving model...")

os.makedirs('models', exist_ok=True)

model.save_model('models/fraud_model_banking.json')
##joblib.dump(model, 'models/fraud_model_banking.pkl')
joblib.dump(scaler, 'models/scaler_banking.pkl')

with open('models/features_banking.json', 'w') as f:
    json.dump(feature_columns, f, indent=2)

config = {
    "model_type": "XGBoost",
    "version": "2.0_improved",
    "trained_date": datetime.now().isoformat(),
    "features_count": len(feature_columns),
    "training_samples": len(X_train),
    "test_auc": float(auc),
    "false_positive_rate": float(false_positive_rate),
    "recommended_threshold": 0.65,
    "default_threshold": 0.65,
    "continuous_features": continuous_features
}

with open('models/model_config_banking.json', 'w') as f:
    json.dump(config, f, indent=2)

print("✅ Saved!")
print("\n" + "="*80)
print("🎉 MODEL TRAINING COMPLETE!")
print("="*80)
print(f"✅ Test AUC: {auc:.4f}")
print(f"✅ False Positive Rate: {false_positive_rate*100:.2f}%")
print("🚀 Ready to use!")
print("="*80)