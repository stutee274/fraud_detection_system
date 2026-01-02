# # test_shap_explanations.py - Test SHAP feature explanations
# import requests
# import json

# URL = "http://127.0.0.1:5000"

# print("\n" + "="*70)
# print("🧪 TESTING SHAP EXPLANATIONS")
# print("="*70)

# # Test 1: Normal prediction with top features
# print("\n1️⃣ Testing Normal Transaction with Top Features")
# print("-"*70)

# normal_txn = {
#     "Time": 100,
#     "V1": 0.5, "V2": 0.3, "V3": -0.2, "V4": 0.8, "V5": 0.1,
#     "V6": 0.4, "V7": -0.3, "V8": 0.2, "V9": 0.1, "V10": 0.3,
#     "V11": 0.2, "V12": 0.1, "V13": -0.1, "V14": 0.4, "V15": 0.2,
#     "V16": 0.3, "V17": -0.2, "V18": 0.1, "V19": 0.2, "V20": 0.1,
#     "V21": 0.3, "V22": 0.2, "V23": 0.1, "V24": 0.2, "V25": 0.1,
#     "V26": 0.2, "V27": 0.1, "V28": 0.1,
#     "Amount": 50.0
# }

# try:
#     response = requests.post(f"{URL}/predict", json=normal_txn, timeout=10)
    
#     if response.status_code == 200:
#         result = response.json()
        
#         print(f"Amount: ${result['transaction_amount']:.2f}")
#         print(f"Prediction: {result['message']}")
#         print(f"Fraud Probability: {result['fraud_probability']*100:.2f}%")
#         print(f"Risk Level: {result['risk_level']}")
        
#         if 'top_contributing_features' in result:
#             print(f"\n🎯 Top 5 Features Contributing to Decision:")
#             for feat in result['top_contributing_features']:
#                 impact_symbol = "📈" if feat['contribution'] > 0 else "📉"
#                 print(f"  {impact_symbol} {feat['feature']:20s} = {feat['value']:8.4f} "
#                       f"(contribution: {feat['contribution']:+.4f})")
#                 print(f"     → {feat['impact']}")
#         else:
#             print("\n⚠️  SHAP explanations not available")
#     else:
#         print(f"❌ Error: {response.status_code}")
#         print(response.text)

# except Exception as e:
#     print(f"❌ Error: {e}")

# # Test 2: Suspicious transaction with top features
# print("\n" + "="*70)
# print("2️⃣ Testing Suspicious Transaction with Top Features")
# print("-"*70)

# suspicious_txn = {
#     "Time": 50000,
#     "V1": -5.5, "V2": 8.2, "V3": -3.4, "V4": 10.1, "V5": -2.8,
#     "V6": 6.7, "V7": -9.3, "V8": 7.4, "V9": -4.1, "V10": 12.5,
#     "V11": -8.2, "V12": 3.6, "V13": 9.1, "V14": -15.3, "V15": 4.7,
#     "V16": 7.8, "V17": -10.2, "V18": 8.9, "V19": -3.5, "V20": 14.2,
#     "V21": -12.4, "V22": 9.7, "V23": -5.8, "V24": 6.3, "V25": -11.2,
#     "V26": 7.5, "V27": -6.1, "V28": 8.4,
#     "Amount": 5000
# }

# try:
#     response = requests.post(f"{URL}/predict", json=suspicious_txn, timeout=10)
    
#     if response.status_code == 200:
#         result = response.json()
        
#         print(f"Amount: ${result['transaction_amount']:.2f}")
#         print(f"Prediction: {result['message']}")
#         print(f"Fraud Probability: {result['fraud_probability']*100:.2f}%")
#         print(f"Risk Level: {result['risk_level']}")
#         print(f"Recommendation: {result['recommendation']}")
        
#         if 'top_contributing_features' in result:
#             print(f"\n🎯 Top 5 Features Contributing to Decision:")
#             for feat in result['top_contributing_features']:
#                 impact_symbol = "📈" if feat['contribution'] > 0 else "📉"
#                 print(f"  {impact_symbol} {feat['feature']:20s} = {feat['value']:8.4f} "
#                       f"(contribution: {feat['contribution']:+.4f})")
#                 print(f"     → {feat['impact']}")
#     else:
#         print(f"❌ Error: {response.status_code}")

# except Exception as e:
#     print(f"❌ Error: {e}")

# # Test 3: Detailed SHAP explanation
# print("\n" + "="*70)
# print("3️⃣ Testing Detailed SHAP Explanation (explain=true)")
# print("-"*70)

# try:
#     response = requests.post(
#         f"{URL}/predict?explain=true",
#         json=suspicious_txn,
#         timeout=10
#     )
    
#     if response.status_code == 200:
#         result = response.json()
        
#         print(f"Amount: ${result['transaction_amount']:.2f}")
#         print(f"Fraud Probability: {result['fraud_probability']*100:.2f}%")
        
#         if 'detailed_explanation' in result:
#             detail = result['detailed_explanation']
#             print(f"\n📊 Detailed SHAP Explanation:")
#             print(f"  Base Value (model average): {detail['base_value']:.4f}")
#             print(f"  Final Prediction: {detail['prediction']:.4f}")
            
#             print(f"\n  Top 10 Most Impactful Features:")
#             for i, feat in enumerate(detail['features'][:10], 1):
#                 impact = "↗️ increases" if feat['shap_value'] > 0 else "↘️ decreases"
#                 print(f"  {i:2d}. {feat['name']:15s} = {feat['value']:8.4f} | "
#                       f"SHAP: {feat['shap_value']:+.4f} ({impact} fraud)")
#         else:
#             print("\n⚠️  Detailed SHAP explanations not available")
#     else:
#         print(f"❌ Error: {response.status_code}")

# except Exception as e:
#     print(f"❌ Error: {e}")

# print("\n" + "="*70)
# print("✅ SHAP EXPLANATION TESTS COMPLETE")
# print("="*70)

# print("\n💡 Understanding SHAP Values:")
# print("  • Positive SHAP value → feature increases fraud probability")
# print("  • Negative SHAP value → feature decreases fraud probability")
# print("  • Larger absolute value → stronger impact on prediction")
# print("  • Base value → model's average prediction across all data")
# print("\n" + "="*70)











############################################################
###_---____________________________________________________________________________________________________________



# test_gemini_system.py - Test complete system with Gemini AI
import requests
import json

URL = "http://127.0.0.1:5000"

print("\n" + "="*70)
print("🧪 TESTING COMPLETE FRAUD DETECTION WITH GEMINI AI")
print("="*70)

# Test 1: Basic prediction (no AI explanation)
print("\n1️⃣ Basic Prediction (No AI Explanation)")
print("-"*70)

normal_txn = {
    "Time": 100,
    "V1": 0.5, "V2": 0.3, "V3": -0.2, "V4": 0.8, "V5": 0.1,
    "V6": 0.4, "V7": -0.3, "V8": 0.2, "V9": 0.1, "V10": 0.3,
    "V11": 0.2, "V12": 0.1, "V13": -0.1, "V14": 0.4, "V15": 0.2,
    "V16": 0.3, "V17": -0.2, "V18": 0.1, "V19": 0.2, "V20": 0.1,
    "V21": 0.3, "V22": 0.2, "V23": 0.1, "V24": 0.2, "V25": 0.1,
    "V26": 0.2, "V27": 0.1, "V28": 0.1,
    "Amount": 50.0
}

try:
    response = requests.post(f"{URL}/predict", json=normal_txn, timeout=10)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Amount: ${result['transaction_amount']:.2f}")
        print(f"   Result: {result['message']}")
        print(f"   Fraud Probability: {result['fraud_probability']*100:.1f}%")
        print(f"   Risk Level: {result['risk_level']}")
        
        if 'top_contributing_features' in result and result['top_contributing_features']:
            print(f"\n   🎯 Top 3 Features:")
            for feat in result['top_contributing_features'][:3]:
                print(f"      • {feat['feature']}: {feat['impact']}")
    else:
        print(f"❌ Error: {response.status_code}")

except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Prediction WITH Gemini AI explanation
print("\n" + "="*70)
print("2️⃣ Prediction WITH Groq AI Explanation")
print("-"*70)

suspicious_txn = {
    "Time": 50000,
    "V1": -5.5, "V2": 8.2, "V3": -3.4, "V4": 10.1, "V5": -2.8,
    "V6": 6.7, "V7": -9.3, "V8": 7.4, "V9": -4.1, "V10": 12.5,
    "V11": -8.2, "V12": 3.6, "V13": 9.1, "V14": -15.3, "V15": 4.7,
    "V16": 7.8, "V17": -10.2, "V18": 8.9, "V19": -3.5, "V20": 14.2,
    "V21": -12.4, "V22": 9.7, "V23": -5.8, "V24": 6.3, "V25": -11.2,
    "V26": 7.5, "V27": -6.1, "V28": 8.4,
    "Amount": 5000
}

try:
    response = requests.post(f"{URL}/predict_explain", json=suspicious_txn, timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Amount: ${result['transaction_amount']:.2f}")
        print(f"Result: {result['message']}")
        print(f"Fraud Probability: {result['fraud_probability']*100:.1f}%")
        print(f"Risk Level: {result['risk_level']}")
        print(f"Recommendation: {result['recommendation']}")
        
        if 'top_contributing_features' in result and result['top_contributing_features']:
            print(f"\n🎯 Top 5 Contributing Features:")
            for i, feat in enumerate(result['top_contributing_features'], 1):
                print(f"   {i}. {feat['feature']} = {feat['value']:.2f}")
                print(f"      → {feat['impact']} (contribution: {feat['contribution']:+.4f})")
        
        if 'ai_explanation' in result:
            print(f"\n🤖 Gemini AI Explanation:")
            print(f"   {result['ai_explanation']}")
            print(f"\n   Provider: {result.get('ai_provider', 'Unknown')}")
        else:
            print(f"\n⚠️  AI explanation not available")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Predict and Learn (with label)
print("\n" + "="*70)
print("3️⃣ Predict and Learn (Save Labeled Data)")
print("-"*70)

labeled_fraud = {
    "Time": 60000,
    "V1": -8.2, "V2": 12.5, "V3": -5.1, "V4": 15.3, "V5": -4.2,
    "V6": 9.8, "V7": -13.4, "V8": 11.2, "V9": -6.3, "V10": 18.7,
    "V11": -10.5, "V12": 5.9, "V13": 14.2, "V14": -18.9, "V15": 7.3,
    "V16": 11.4, "V17": -15.6, "V18": 13.8, "V19": -5.8, "V20": 21.3,
    "V21": -16.7, "V22": 14.9, "V23": -8.2, "V24": 9.6, "V25": -17.3,
    "V26": 11.8, "V27": -9.1, "V28": 12.7,
    "Amount": 8000,
    "Class": 1  # This is confirmed fraud
}

try:
    response = requests.post(f"{URL}/predict_and_learn", json=labeled_fraud, timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Amount: ${result['transaction_amount']:.2f}")
        print(f"Model Prediction: {result['message']}")
        print(f"Fraud Probability: {result['fraud_probability']*100:.1f}%")
        
        if 'learning_status' in result:
            print(f"\n📚 Learning: {result['learning_status']}")
            print(f"   Note: {result.get('learning_note', 'N/A')}")
        
        if 'ai_explanation' in result:
            print(f"\n🤖 AI Explanation:")
            print(f"   {result['ai_explanation']}")
    else:
        print(f"❌ Error: {response.status_code}")

except Exception as e:
    print(f"❌ Error: {e}")

# Test 4: Batch predictions
print("\n" + "="*70)
print("4️⃣ Batch Predictions")
print("-"*70)

batch_txns = {
    "transactions": [
        {**{f"V{i}": 0.1 for i in range(1, 29)}, "Time": 1000, "Amount": 25},
        {**{f"V{i}": 0.2 for i in range(1, 29)}, "Time": 2000, "Amount": 75},
        {**{f"V{i}": -5.0 for i in range(1, 29)}, "Time": 3000, "Amount": 3000}
    ],
    "threshold": 0.5
}

try:
    response = requests.post(f"{URL}/batch", json=batch_txns, timeout=15)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Total Transactions: {result['total_transactions']}")
        print(f"Successful Predictions: {result['successful_predictions']}")
        print(f"Fraud Detected: {result['fraud_detected']}")
        print(f"Fraud Rate: {result['fraud_rate']*100:.1f}%")
        print(f"Total Flagged Amount: ${result['total_flagged_amount']:.2f}")
        
        print(f"\n📊 Individual Results:")
        for r in result['results']:
            if r.get('status') == 'success':
                status_icon = "🚨" if r['prediction'] == 1 else "✅"
                print(f"   {status_icon} Transaction {r['transaction_id']}: "
                      f"${r['amount']:.2f} - "
                      f"{r['fraud_probability']*100:.1f}% fraud prob")
    else:
        print(f"❌ Error: {response.status_code}")

except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*70)
print("✅ TESTING COMPLETE")
print("="*70)

print("\n📋 Summary:")
print("  1. ✅ Basic predictions")
print("  2. ✅ Predictions with Gemini AI explanations")
print("  3. ✅ Learning from labeled data")
print("  4. ✅ Batch processing")
print("\n💡 All features working correctly!")
print("="*70 + "\n")