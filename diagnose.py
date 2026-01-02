# # diagnose_prediction_issue.py - Find why all predictions are 0.3577
# import pandas as pd
# import json
# import joblib
# from xgboost import XGBClassifier
# from features.features_eng import engineer_features
# import numpy as np

# print("\n" + "="*70)
# print("🔍 DIAGNOSING PREDICTION ISSUE")
# print("="*70)

# # Load model
# print("\n1️⃣ Loading model...")
# model = XGBClassifier()
# try:
#     model.load_model("models/fraud_model_improved.json")
#     print("✅ Loaded: fraud_model_improved.json")
# except:
#     model.load_model("models/fraud_model.json")
#     print("⚠️  Loaded: fraud_model.json")

# # Load scaler and features
# amount_scaler = joblib.load("models/amount_scaler.pkl")
# with open("models/features.json") as f:
#     FEATURES = json.load(f)

# print(f"✅ Features: {len(FEATURES)}")

# # Test transactions with DIFFERENT amounts
# print("\n" + "="*70)
# print("2️⃣ Testing 3 Transactions with Different Amounts")
# print("="*70)

# test_transactions = [
#     {
#         "name": "Small Normal",
#         "Time": 10000,
#         "Amount": 50,
#         "V1": 0.5, "V2": 0.3, "V3": -0.2, "V4": 0.8, "V5": 0.1,
#         "V6": 0.4, "V7": -0.3, "V8": 0.2, "V9": 0.1, "V10": 0.3,
#         "V11": 0.2, "V12": 0.1, "V13": -0.1, "V14": 0.4, "V15": 0.2,
#         "V16": 0.3, "V17": -0.2, "V18": 0.1, "V19": 0.2, "V20": 0.1,
#         "V21": 0.3, "V22": 0.2, "V23": 0.1, "V24": 0.2, "V25": 0.1,
#         "V26": 0.2, "V27": 0.1, "V28": 0.1
#     },
#     {
#         "name": "Large Suspicious",
#         "Time": 50000,
#         "Amount": 5000,
#         "V1": -5.5, "V2": 8.2, "V3": -3.4, "V4": 10.1, "V5": -2.8,
#         "V6": 6.7, "V7": -9.3, "V8": 7.4, "V9": -4.1, "V10": 12.5,
#         "V11": -8.2, "V12": 3.6, "V13": 9.1, "V14": -15.3, "V15": 4.7,
#         "V16": 7.8, "V17": -10.2, "V18": 8.9, "V19": -3.5, "V20": 14.2,
#         "V21": -12.4, "V22": 9.7, "V23": -5.8, "V24": 6.3, "V25": -11.2,
#         "V26": 7.5, "V27": -6.1, "V28": 8.4
#     },
#     {
#         "name": "Very Large",
#         "Time": 86400,
#         "Amount": 12500,
#         "V1": -12.5, "V2": 18.3, "V3": -7.8, "V4": 22.1, "V5": -6.4,
#         "V6": 14.2, "V7": -19.7, "V8": 16.8, "V9": -9.2, "V10": 25.4,
#         "V11": -15.3, "V12": 8.7, "V13": 20.5, "V14": -24.6, "V15": 11.2,
#         "V16": 17.9, "V17": -21.3, "V18": 19.4, "V19": -8.9, "V20": 28.7,
#         "V21": -22.1, "V22": 20.3, "V23": -12.4, "V24": 14.8, "V25": -23.9,
#         "V26": 16.5, "V27": -13.7, "V28": 18.2
#     }
# ]

# results = []

# for txn in test_transactions:
#     name = txn.pop("name")
    
#     print(f"\n{'='*70}")
#     print(f"Testing: {name}")
#     print(f"{'='*70}")
    
#     # Create DataFrame
#     df = pd.DataFrame([txn])
    
#     print(f"Original Amount: ${df['Amount'].values[0]:.2f}")
#     print(f"Original V14: {df['V14'].values[0]:.2f}")
#     print(f"Original V10: {df['V10'].values[0]:.2f}")
    
#     # Feature engineering
#     df_eng = engineer_features(df)
    
#     print(f"\nAfter Feature Engineering:")
#     print(f"  Amount: {df_eng['Amount'].values[0]:.2f}")
#     print(f"  Amount_log: {df_eng['Amount_log'].values[0]:.4f}")
#     print(f"  amount_roll_mean_3: {df_eng['amount_roll_mean_3'].values[0]:.2f}")
#     print(f"  Hour: {df_eng['Hour'].values[0]}")
    
#     # Scale Amount
#     df_eng["Amount"] = amount_scaler.transform(df_eng[["Amount"]])
    
#     print(f"  Amount (scaled): {df_eng['Amount'].values[0]:.4f}")
    
#     # Ensure features
#     for col in FEATURES:
#         if col not in df_eng.columns:
#             df_eng[col] = 0
    
#     X = df_eng[FEATURES]
    
#     # Predict
#     proba = model.predict_proba(X)[0][1]
#     pred = int(proba >= 0.5)
    
#     print(f"\n🎯 Result:")
#     print(f"  Fraud Probability: {proba:.4f} ({proba*100:.2f}%)")
#     print(f"  Prediction: {pred} ({'FRAUD' if pred else 'NORMAL'})")
    
#     results.append({
#         'name': name,
#         'amount': txn['Amount'],
#         'v14': txn['V14'],
#         'probability': proba,
#         'prediction': pred
#     })

# # Summary
# print("\n" + "="*70)
# print("📊 SUMMARY")
# print("="*70)

# summary_df = pd.DataFrame(results)
# print(summary_df.to_string(index=False))

# # Check if all probabilities are the same
# unique_probs = summary_df['probability'].nunique()

# if unique_probs == 1:
#     print(f"\n❌ PROBLEM FOUND!")
#     print(f"   All {len(results)} transactions have IDENTICAL probability: {results[0]['probability']:.4f}")
#     print(f"\n🔍 Likely causes:")
#     print(f"   1. Feature engineering creates identical features")
#     print(f"   2. amount_roll_mean_3 equals raw Amount (no real rolling average)")
#     print(f"   3. Model relies too heavily on one feature")
#     print(f"\n💡 Solution:")
#     print(f"   - Fix features_eng.py to create proper rolling features")
#     print(f"   - Or lower threshold to 0.3 to catch these transactions")
# else:
#     print(f"\n✅ GOOD!")
#     print(f"   Found {unique_probs} different probabilities")
#     print(f"   Model is distinguishing between transactions")

# # Feature importance check
# print("\n" + "="*70)
# print("🔍 TOP 5 FEATURE IMPORTANCES")
# print("="*70)

# feature_importance = pd.DataFrame({
#     'feature': FEATURES,
#     'importance': model.feature_importances_
# }).sort_values('importance', ascending=False).head(5)

# print(feature_importance.to_string(index=False))

# dominant_feature = feature_importance.iloc[0]
# if dominant_feature['importance'] > 0.3:
#     print(f"\n⚠️  WARNING: '{dominant_feature['feature']}' has {dominant_feature['importance']*100:.1f}% importance")
#     print(f"   Model relies too heavily on this one feature!")

# print("\n" + "="*70 + "\n")



# diagnose_dataset.py - Check why model has 99.8% precision
"""
Analyzes the dataset to find if:
1. Features are too predictive (data leakage)
2. Fraud patterns are too obvious
3. Dataset is synthetic and unrealistic
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

print("="*80)
print("🔍 DATASET DIAGNOSIS")
print("="*80)

# Load dataset
df = pd.read_csv(r"data\synthetic_fraud.csv")

print(f"\n📊 DATASET OVERVIEW:")
print(f"   Total transactions: {len(df):,}")
print(f"   Fraud: {df['Fraud_Label'].sum():,} ({df['Fraud_Label'].mean()*100:.2f}%)")
print(f"   Normal: {(~df['Fraud_Label'].astype(bool)).sum():,} ({(~df['Fraud_Label'].astype(bool)).mean()*100:.2f}%)")

# ============================================
# CHECK FOR DATA LEAKAGE
# ============================================
print("\n\n🚨 CHECKING FOR DATA LEAKAGE:")
print("="*80)

# Check if Risk_Score is too correlated with fraud
risk_fraud_corr = df[['Risk_Score', 'Fraud_Label']].corr().iloc[0, 1]
print(f"\n1. Risk_Score correlation with Fraud: {risk_fraud_corr:.4f}")
if abs(risk_fraud_corr) > 0.7:
    print(f"   ⚠️  WARNING: Risk_Score is highly correlated with fraud!")
    print(f"   This suggests Risk_Score was calculated AFTER knowing fraud label")
    print(f"   (Data leakage!)")
else:
    print(f"   ✅ Risk_Score correlation looks reasonable")

# Check fraud rate by Risk_Score
print(f"\n2. Fraud rate by Risk_Score bucket:")
df['risk_bucket'] = pd.cut(df['Risk_Score'], bins=[0, 0.3, 0.5, 0.7, 1.0], 
                            labels=['Low', 'Medium', 'High', 'Critical'])
fraud_by_risk = df.groupby('risk_bucket')['Fraud_Label'].agg(['mean', 'count'])
print(fraud_by_risk)
print()

if fraud_by_risk.loc['Critical', 'mean'] > 0.8:
    print(f"   ⚠️  WARNING: {fraud_by_risk.loc['Critical', 'mean']*100:.1f}% of 'Critical' risk are fraud!")
    print(f"   This is TOO PERFECT - suggests data leakage")

# Check Failed_Transaction_Count_7d
print(f"\n3. Failed transactions vs Fraud:")
failed_fraud = df.groupby('Failed_Transaction_Count_7d')['Fraud_Label'].mean()
print(f"   Avg fraud rate with 0 failures: {failed_fraud.get(0, 0)*100:.1f}%")
print(f"   Avg fraud rate with 4+ failures: {df[df['Failed_Transaction_Count_7d'] >= 4]['Fraud_Label'].mean()*100:.1f}%")

# Check Previous_Fraudulent_Activity
print(f"\n4. Previous fraud history:")
prev_fraud_rate = df.groupby('Previous_Fraudulent_Activity')['Fraud_Label'].mean()
print(f"   Fraud rate with no history: {prev_fraud_rate.get(0, 0)*100:.1f}%")
print(f"   Fraud rate with history: {prev_fraud_rate.get(1, 0)*100:.1f}%")

if prev_fraud_rate.get(1, 0) > 0.8:
    print(f"   ⚠️  WARNING: {prev_fraud_rate.get(1, 0)*100:.1f}% of transactions with fraud history are fraud!")
    print(f"   This is unrealistic - real fraudsters change patterns")

# ============================================
# CHECK FEATURE SEPARABILITY
# ============================================
print("\n\n📐 FEATURE SEPARABILITY:")
print("="*80)

important_features = [
    'Risk_Score', 
    'Failed_Transaction_Count_7d',
    'Previous_Fraudulent_Activity',
    'Transaction_Amount',
    'Account_Balance',
    'Daily_Transaction_Count'
]

print("\nMean values by fraud status:")
print("-"*80)
comparison = df.groupby('Fraud_Label')[important_features].mean()
print(comparison.T)

print("\n\n🎯 DIAGNOSIS SUMMARY:")
print("="*80)

issues = []

if abs(risk_fraud_corr) > 0.7:
    issues.append("Risk_Score shows data leakage")

if fraud_by_risk.loc['Critical', 'mean'] > 0.8:
    issues.append("Critical risk score is perfect predictor")

if prev_fraud_rate.get(1, 0) > 0.8:
    issues.append("Previous fraud history is perfect predictor")

if df[df['Failed_Transaction_Count_7d'] >= 4]['Fraud_Label'].mean() > 0.8:
    issues.append("Failed transaction count is perfect predictor")

if issues:
    print("\n⚠️  ISSUES FOUND:")
    for i, issue in enumerate(issues, 1):
        print(f"   {i}. {issue}")
    
    print("\n🔧 RECOMMENDATIONS:")
    print("   1. Remove Risk_Score (it knows the answer!)")
    print("   2. Remove Previous_Fraudulent_Activity (too perfect)")
    print("   3. Add noise to Failed_Transaction_Count_7d")
    print("   4. Train without 'leaky' features")
    
else:
    print("\n✅ Dataset looks realistic!")

# ============================================
# CALCULATE EXPECTED PERFORMANCE
# ============================================
print("\n\n📊 EXPECTED MODEL PERFORMANCE:")
print("="*80)

# If we just predict fraud when Risk_Score > 0.7
simple_pred = (df['Risk_Score'] > 0.7).astype(int)
simple_accuracy = (simple_pred == df['Fraud_Label']).mean()
simple_recall = (simple_pred & df['Fraud_Label']).sum() / df['Fraud_Label'].sum()
simple_precision = (simple_pred & df['Fraud_Label']).sum() / simple_pred.sum() if simple_pred.sum() > 0 else 0

print(f"\nSimple rule: 'Fraud if Risk_Score > 0.7'")
print(f"   Accuracy:  {simple_accuracy*100:.1f}%")
print(f"   Recall:    {simple_recall*100:.1f}%")
print(f"   Precision: {simple_precision*100:.1f}%")

if simple_precision > 0.95:
    print(f"\n⚠️  A simple rule achieves {simple_precision*100:.1f}% precision!")
    print(f"   This means the dataset is TOO EASY")
    print(f"   Real-world fraud is much harder to detect")

print("\n" + "="*80)
print("✅ DIAGNOSIS COMPLETE")
print("="*80)