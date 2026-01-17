# genai_dual.py - Enhanced GenAI explainer for Credit Card and Banking fraud
from groq import Groq
from dotenv import load_dotenv
import hashlib, json, os

# Load environment
load_dotenv(".env")
API_KEY = os.getenv("GROQ_API_KEY")

if API_KEY:
    client = Groq(api_key=API_KEY)
    GROQ_AVAILABLE = True
else:
    print("⚠️  GROQ_API_KEY not found - using fallback explanations")
    GROQ_AVAILABLE = False

MODEL_NAME = "llama-3.3-70b-versatile"
CACHE_FILE = "genai_cache.json"
CACHE = json.load(open(CACHE_FILE)) if os.path.exists(CACHE_FILE) else {}

# ============================================
# FEATURE MEANINGS - BANKING
# ============================================
BANKING_FEATURES = {
    # Time patterns
    "late_night": "transaction during late night (10 PM - 6 AM)",
    "early_morning": "transaction during early morning (midnight - 4 AM)",
    "midnight": "transaction exactly at midnight",
    "business_hours": "transaction during business hours (9 AM - 5 PM)",
    "Hour": "hour of transaction",
    "Is_Weekend": "weekend transaction",
    
    # Amount patterns
    "Transaction_Amount": "transaction amount",
    "spend_ratio": "spending ratio vs available balance",
    "amount_vs_avg": "amount compared to 7-day average",
    "large_amount": "unusually large transaction",
    "very_large": "extremely large transaction",
    "amount_high": "high amount flag",
    
    # Balance patterns
    "Account_Balance": "current account balance",
    "low_balance": "low account balance",
    "very_low_balance": "critically low balance",
    
    # Transaction type
    "is_atm": "ATM withdrawal",
    "is_online": "online transaction",
    "is_pos": "point-of-sale transaction",
    "is_transfer": "bank transfer",
    
    # Activity patterns
    "Daily_Transaction_Count": "transactions today",
    "high_daily_count": "unusually high transaction frequency",
    "Failed_Transaction_Count_7d": "failed transactions in last 7 days",
    "any_failed": "has recent failed transactions",
    "high_failed": "high number of failed transactions",
    "velocity_alert": "rapid transactions with failures",
    
    # Card patterns
    "Card_Age": "card age in days",
    "new_card": "newly issued card (< 30 days)",
    "very_new_card": "very new card (< 15 days)",
    "old_card": "established card (> 180 days)",
    
    # Location patterns
    "Transaction_Distance": "distance from usual location (km)",
    "far_transaction": "transaction far from home",
    "very_far": "transaction very far from home",
    "suspicious_ip": "suspicious IP address",
    
    # Combined risk patterns
    "night_high_spend": "late night + high spending",
    "night_large_amount": "late night + large amount",
    "distance_night": "far location + late night",
    "suspicious_combo": "suspicious IP + late night",
    "atm_night_far": "ATM + night + far from home",
    "online_night": "online purchase late at night",
    "new_card_large": "new card + large purchase",
    "weekend_night": "weekend + late night",
}

# ============================================
# FEATURE MEANINGS - CREDIT CARD
# ============================================
CREDIT_CARD_FEATURES = {
    # V features (PCA components)
    "V1": "payment pattern component 1",
    "V2": "transaction characteristic",
    "V3": "spending behavior pattern",
    "V4": "payment method signal",
    "V5": "transaction pattern 5",
    "V6": "behavioral indicator 6",
    "V7": "transaction pattern 7",
    "V8": "fraud pattern 8",
    "V9": "transaction signal 9",
    "V10": "secondary fraud pattern (high importance)",
    "V11": "transaction pattern 11",
    "V12": "unusual activity marker",
    "V13": "transaction pattern 13",
    "V14": "primary fraud indicator (highest importance)",
    "V15": "transaction pattern 15",
    "V16": "fraud signal 16",
    "V17": "fraud pattern detector",
    "V18": "transaction pattern 18",
    "V19": "behavioral signal 19",
    "V20": "transaction pattern 20",
    "V21": "fraud indicator 21",
    "V22": "transaction pattern 22",
    "V23": "behavioral pattern 23",
    "V24": "transaction signal 24",
    "V25": "fraud pattern 25",
    "V26": "transaction pattern 26",
    "V27": "behavioral indicator 27",
    "V28": "fraud signal 28",
    
    # Time and amount
    "Amount": "transaction amount",
    "Amount_log": "logarithmic amount (detects large transactions)",
    "Hour": "transaction hour",
    "Time": "seconds since first transaction",
}

def explain_transaction(top_features, fraud_prob, amount, model_type="banking"):
    """
    Generate fraud explanation using Groq AI
    
    Args:
        top_features: List of dicts [{"feature": name, "value": val, "shap_value": contrib, "impact": "increases/decreases"}, ...]
        fraud_prob: Float between 0 and 1
        amount: Transaction amount
        model_type: "credit_card" or "banking"
        
    Returns:
        String explanation
    """
    
    # Select feature dictionary
    feature_dict = CREDIT_CARD_FEATURES if model_type == "credit_card" else BANKING_FEATURES
    
    # Cache key
    key_raw = json.dumps(top_features, sort_keys=True) + str(round(fraud_prob, 2)) + model_type
    cache_key = hashlib.md5(key_raw.encode()).hexdigest()
    
    if cache_key in CACHE:
        return CACHE[cache_key]
    
    # Build feature analysis
    feature_text = ""
    risk_factors = []
    
    for i, feat in enumerate(top_features[:5], 1):
        feature_name = feat["feature"]
        value = feat["value"]
        contribution = feat["shap_value"]
        impact = feat["impact"]
        
        meaning = feature_dict.get(feature_name, "transaction signal")
        direction = "🔴 RISK" if contribution > 0 else "✅ SAFE"
        
        feature_text += f"{i}. {feature_name} = {value:.2f} | {meaning}\n"
        feature_text += f"   Impact: {contribution:+.4f} | {direction}\n"
        
        # Collect human-readable risk factors
        if contribution > 0 and impact == "increases":
            if "night" in feature_name.lower():
                risk_factors.append("late night transaction")
            elif "failed" in feature_name.lower():
                risk_factors.append("history of failed transactions")
            elif "new_card" in feature_name.lower():
                risk_factors.append("newly issued card")
            elif "distance" in feature_name.lower() or "far" in feature_name.lower():
                risk_factors.append("unusual location")
            elif "large" in feature_name.lower() or "amount" in feature_name.lower():
                risk_factors.append("unusually large amount")
            elif "velocity" in feature_name.lower() or "high_daily" in feature_name.lower():
                risk_factors.append("high transaction frequency")
            elif "suspicious" in feature_name.lower():
                risk_factors.append("suspicious IP/location")
    
    # Create prompt
    if not GROQ_AVAILABLE:
        return _fallback_explanation(fraud_prob, amount, risk_factors, model_type)
    
    prompt = f"""You are a senior fraud analyst. Analyze this transaction in exactly 80-100 words.

TRANSACTION:
• Amount: ${amount:,.2f}
• Fraud Risk: {fraud_prob:.1%}
• Model: {model_type.replace('_', ' ').title()}

TOP RISK FACTORS:
{feature_text}

PATTERNS DETECTED:
{', '.join(risk_factors[:3]) if risk_factors else 'Normal patterns'}

YOUR ANALYSIS (80-100 words):
{"Explain WHY this is fraud. Mention:" if fraud_prob >= 0.5 else "Explain WHY this is legitimate. Mention:"}
1. The TOP 2 risk factors specifically
2. What makes this {'suspicious' if fraud_prob >= 0.5 else 'normal'} (timing, amount, location, card age, etc.)
3. Clear recommendation: {'Block' if fraud_prob >= 0.7 else 'Review' if fraud_prob >= 0.5 else 'Approve'}

Write as a professional fraud analyst. Be specific and detailed.

EXPLANATION:"""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=150
        )
        
        explanation = response.choices[0].message.content.strip()
        
        # Cache it
        CACHE[cache_key] = explanation
        json.dump(CACHE, open(CACHE_FILE, "w"), indent=2)
        
        return explanation
        
    except Exception as e:
        print(f"⚠️  Groq API error: {e}")
        return _fallback_explanation(fraud_prob, amount, risk_factors, model_type)


def _fallback_explanation(fraud_prob, amount, risk_factors, model_type):
    """Fallback explanation when API unavailable - 100 words"""
    
    if fraud_prob >= 0.7:
        risk_level = "CRITICAL"
        action = "BLOCK IMMEDIATELY"
    elif fraud_prob >= 0.5:
        risk_level = "HIGH"
        action = "BLOCK AND REVIEW"
    elif fraud_prob >= 0.3:
        risk_level = "MEDIUM"
        action = "FLAG FOR REVIEW"
    else:
        risk_level = "LOW"
        action = "APPROVE"
    
    if fraud_prob >= 0.5:
        # Fraud explanation (100 words)
        factors_text = ", ".join(risk_factors[:3]) if risk_factors else "suspicious patterns"
        return f"⚠️ **FRAUD ALERT** ({fraud_prob:.1%} confidence)\n\n" \
               f"This ${amount:,.2f} transaction exhibits **{risk_level} RISK** characteristics. " \
               f"Key indicators include: {factors_text}. " \
               f"The transaction pattern deviates significantly from normal customer behavior. " \
               f"Multiple fraud signals detected across timing, amount, and location parameters. " \
               f"The combination of these factors suggests unauthorized account access or compromised card credentials. " \
               f"This warrants immediate intervention to prevent potential financial loss.\n\n" \
               f"**Recommended Action:** {action}"
    else:
        # Normal explanation (100 words)
        return f"✅ **LEGITIMATE TRANSACTION** ({(1-fraud_prob):.1%} confidence)\n\n" \
               f"This ${amount:,.2f} transaction demonstrates normal spending patterns consistent with legitimate customer activity. " \
               f"The transaction timing, amount, and location all fall within expected parameters. " \
               f"No significant fraud indicators detected. The customer's transaction history shows consistent behavior patterns. " \
               f"Account activity remains within normal velocity thresholds. Card usage location matches historical patterns. " \
               f"Risk assessment indicates standard consumer transaction behavior.\n\n" \
               f"**Risk Level:** {risk_level}\n" \
               f"**Recommended Action:** {action}"


# ============================================
# TEST
# ============================================
if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 TESTING DUAL GENAI EXPLAINER")
    print("="*70)
    
    # Test Banking Model
    print("\n1️⃣ BANKING MODEL - Fraud Transaction")
    banking_features = [
        {"feature": "late_night", "value": 1.0, "shap_value": 0.234, "impact": "increases"},
        {"feature": "Failed_Transaction_Count_7d", "value": 5.0, "shap_value": 0.187, "impact": "increases"},
        {"feature": "night_high_spend", "value": 1.0, "shap_value": 0.156, "impact": "increases"},
        {"feature": "very_far", "value": 1.0, "shap_value": 0.112, "impact": "increases"},
    ]
    
    explanation = explain_transaction(banking_features, 0.83, 8000, "banking")
    print(f"\nAmount: $8,000")
    print(f"Fraud Probability: 83%")
    print(f"\nExplanation:\n{explanation}")
    
    # Test Credit Card Model
    print("\n" + "="*70)
    print("2️⃣ CREDIT CARD MODEL - Normal Transaction")
    cc_features = [
        {"feature": "V14", "value": 0.5, "shap_value": -0.123, "impact": "decreases"},
        {"feature": "V10", "value": 0.3, "shap_value": -0.089, "impact": "decreases"},
        {"feature": "Amount", "value": 75.0, "shap_value": -0.045, "impact": "decreases"},
    ]
    
    explanation = explain_transaction(cc_features, 0.12, 75, "credit_card")
    print(f"\nAmount: $75")
    print(f"Fraud Probability: 12%")
    print(f"\nExplanation:\n{explanation}")
    
    print("\n" + "="*70)
    print("✅ Testing Complete")
    print("="*70 + "\n")