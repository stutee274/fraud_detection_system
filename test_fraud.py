# test_real_fraud_samples.py - Test with ACTUAL fraud from dataset
import pandas as pd
import requests
import json

print("\n" + "="*70)
print("🧪 TESTING WITH REAL FRAUD SAMPLES FROM DATASET")
print("="*70)

# Load dataset
print("\n📂 Loading creditcard.csv...")
df = pd.read_csv("data/creditcard.csv")

# Get real fraud samples
frauds = df[df["Class"] == 1].head(5)
normals = df[df["Class"] == 0].head(3)

print(f"✅ Found {len(frauds)} real fraud samples")
print(f"✅ Found {len(normals)} real normal samples")

URL = "http://127.0.0.1:5000"

# Test with real frauds
print("\n" + "="*70)
print("🚨 TESTING REAL FRAUD TRANSACTIONS")
print("="*70)

for idx, row in frauds.iterrows():
    # Convert row to dict (exclude Class for prediction)
    transaction = row.drop("Class").to_dict()
    
    # Add Class back for learning
    transaction["Class"] = 1
    
    print(f"\n{'='*70}")
    print(f"Real Fraud #{idx + 1}")
    print(f"{'='*70}")
    print(f"Amount: ${row['Amount']:.2f}")
    print(f"V14: {row['V14']:.2f}, V17: {row['V17']:.2f}, V10: {row['V10']:.2f}")
    
    try:
        response = requests.post(
            f"{URL}/predict_explain",
            json=transaction,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            fraud_prob = result['fraud_probability']
            prediction = result['prediction']
            risk_level = result['risk_level']
            
            # Check if model caught it
            if prediction == 1:
                status = "✅ CAUGHT"
                color = "GREEN"
            else:
                status = "❌ MISSED"
                color = "RED"
            
            print(f"\nModel Result:")
            print(f"  Fraud Probability: {fraud_prob*100:.1f}%")
            print(f"  Prediction: {prediction} ({result['message']})")
            print(f"  Risk Level: {risk_level}")
            print(f"  Status: {status}")
            
            if 'top_contributing_features' in result:
                print(f"\n  Top 3 Features:")
                for feat in result['top_contributing_features'][:3]:
                    print(f"    • {feat['feature']}: {feat['value']:.2f} (contrib: {feat['contribution']:+.4f})")
            
            if 'ai_explanation' in result:
                print(f"\n  🤖 AI: {result['ai_explanation'][:200]}...")
        
        else:
            print(f"  ❌ Error: {response.status_code}")
    
    except Exception as e:
        print(f"  ❌ Error: {e}")

# Test with real normals
print("\n" + "="*70)
print("✅ TESTING REAL NORMAL TRANSACTIONS")
print("="*70)

for idx, row in normals.iterrows():
    transaction = row.drop("Class").to_dict()
    transaction["Class"] = 0
    
    print(f"\n{'='*70}")
    print(f"Real Normal #{idx + 1}")
    print(f"{'='*70}")
    print(f"Amount: ${row['Amount']:.2f}")
    
    try:
        response = requests.post(
            f"{URL}/predict_explain",
            json=transaction,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            fraud_prob = result['fraud_probability']
            prediction = result['prediction']
            
            # Check if correctly identified as normal
            if prediction == 0:
                status = "✅ CORRECT"
            else:
                status = "⚠️ FALSE ALARM"
            
            print(f"\nModel Result:")
            print(f"  Fraud Probability: {fraud_prob*100:.1f}%")
            print(f"  Prediction: {prediction} ({result['message']})")
            print(f"  Status: {status}")
        
        else:
            print(f"  ❌ Error: {response.status_code}")
    
    except Exception as e:
        print(f"  ❌ Error: {e}")

print("\n" + "="*70)
print("✅ TESTING COMPLETE")
print("="*70)
print("\n💡 Summary:")
print("  - If frauds are CAUGHT with high probability (>60%) → Model is working")
print("  - If frauds are MISSED or have low probability → Feature engineering issue")
print("  - If all frauds have SAME probability → Definite bug")
print("="*70 + "\n")