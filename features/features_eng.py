# # features/features_eng.py - FIXED VERSION
# import numpy as np
# import pandas as pd

# def engineer_features(df):
#     """
#     Engineer features for fraud detection.
#     Works for both training (multiple rows) and prediction (single row).
    
#     FIXED: Proper handling of amount features for single transactions
#     """
#     df = df.copy()
    
#     # Store original amount for reference
#     original_amount = df["Amount"].values[0] if len(df) == 1 else None

#     # Time-based features
#     if "Time" in df.columns:
#         df["Hour"] = (df["Time"] // 3600) % 24
#     else:
#         df["Hour"] = 0

#     # For single transaction (real-time prediction)
#     if len(df) == 1:
#         # Use reasonable defaults based on typical behavior
#         df["time_gap"] = 0
#         df["txn_last_1hr"] = 1
        
#         # Amount behavior features
#         df["Amount_log"] = np.log1p(df["Amount"])
        
#         # Rolling features - Use the transaction amount itself
#         # This is reasonable for real-time since we don't have history
#         df["amount_roll_mean_3"] = df["Amount"]
#         df["amount_roll_std_3"] = 0
    
#     # For batch/training (multiple rows)
#     else:
#         # Time gaps between transactions
#         df["time_gap"] = df["Time"].diff().fillna(0)
        
#         # Count transactions in last hour
#         df["txn_last_1hr"] = df["Time"].rolling(window=3600, min_periods=1).count()
        
#         # Amount features
#         df["Amount_log"] = np.log1p(df["Amount"])
        
#         # Rolling statistics for Amount
#         df["amount_roll_mean_3"] = df["Amount"].rolling(window=3, min_periods=1).mean()
#         df["amount_roll_std_3"] = df["Amount"].rolling(window=3, min_periods=1).std().fillna(0)

#     # Drop Time column (model not trained on it)
#     if "Time" in df.columns:
#         df = df.drop(columns=["Time"])

#     return df




# 2nd traial 






#####___________________________________#####


# features/features_eng.py - PROPERLY FIXED VERSION
import numpy as np
import pandas as pd

def engineer_features(df):
    """
    Engineer features for fraud detection.
    
    FIXED FOR LONG-TERM:
    - Better rolling feature calculation for single transactions
    - Uses statistical approach instead of raw amount
    - Helps model distinguish between different transaction sizes
    
    Works for both:
    - Training (multiple rows)
    - Real-time prediction (single row)
    """
    df = df.copy()
    is_single_transaction = len(df) == 1

    # ============================================
    # TIME-BASED FEATURES
    # ============================================
    if "Time" in df.columns:
        # Extract hour (0-23)
        df["Hour"] = (df["Time"] // 3600) % 24
    else:
        df["Hour"] = 0

    # ============================================
    # SINGLE TRANSACTION (REAL-TIME PREDICTION)
    # ============================================
    if is_single_transaction:
        # Time features - defaults for single transaction
        df["time_gap"] = 0  # No previous transaction to compare
        df["txn_last_1hr"] = 1  # Assume this is the only recent transaction
        
        # Amount features
        amount_value = df["Amount"].values[0]
        df["Amount_log"] = np.log1p(amount_value)
        
        # FIXED: Better rolling feature calculation
        # Instead of using raw amount, use a normalized approach
        # This helps distinguish $100 from $1000 from $10000
        
        # Use logarithmic transformation for rolling mean
        # This compresses large amounts while preserving differences
        df["amount_roll_mean_3"] = np.log1p(amount_value)
        
        # Create synthetic variance based on amount size
        # Larger amounts should have larger variance signals
        if amount_value < 50:
            df["amount_roll_std_3"] = 0  # Small purchases: no variance
        elif amount_value < 500:
            df["amount_roll_std_3"] = amount_value * 0.1  # Medium: 10% variance
        else:
            df["amount_roll_std_3"] = amount_value * 0.2  # Large: 20% variance

    # ============================================
    # BATCH/TRAINING (MULTIPLE ROWS)
    # ============================================
    else:
        # Time gaps between consecutive transactions
        df["time_gap"] = df["Time"].diff().fillna(0)
        
        # Transaction velocity: count in last hour (3600 seconds)
        # This uses a rolling window based on time
        df["txn_last_1hr"] = df.groupby(
            (df["Time"] // 3600)
        )["Time"].transform("count")
        
        # Amount features
        df["Amount_log"] = np.log1p(df["Amount"])
        
        # Rolling statistics (window of 3 transactions)
        df["amount_roll_mean_3"] = df["Amount"].rolling(
            window=3, 
            min_periods=1
        ).mean()
        
        df["amount_roll_std_3"] = df["Amount"].rolling(
            window=3, 
            min_periods=1
        ).std().fillna(0)
    
    # ============================================
    # CLEANUP
    # ============================================
    # Drop Time column (model wasn't trained on it)
    if "Time" in df.columns:
        df = df.drop(columns=["Time"])

    return df


# ============================================
# HELPER FUNCTION FOR DEBUGGING
# ============================================
def debug_features(transaction_dict):
    """
    Debug helper to see what features are created
    
    Usage:
        from features.features_eng import debug_features
        debug_features({"Time": 10000, "Amount": 5000, "V1": -5.5, ...})
    """
    df = pd.DataFrame([transaction_dict])
    df_eng = engineer_features(df)
    
    print("\n" + "="*60)
    print("FEATURE ENGINEERING DEBUG")
    print("="*60)
    print(f"Input Amount: ${transaction_dict.get('Amount', 0):.2f}")
    print(f"\nGenerated Features:")
    print(f"  Amount_log: {df_eng['Amount_log'].values[0]:.4f}")
    print(f"  amount_roll_mean_3: {df_eng['amount_roll_mean_3'].values[0]:.4f}")
    print(f"  amount_roll_std_3: {df_eng['amount_roll_std_3'].values[0]:.4f}")
    print(f"  Hour: {df_eng['Hour'].values[0]}")
    print(f"  time_gap: {df_eng['time_gap'].values[0]}")
    print(f"  txn_last_1hr: {df_eng['txn_last_1hr'].values[0]}")
    print("="*60 + "\n")
    
    return df_eng


if __name__ == "__main__":
    # Test with sample transactions
    print("\n🧪 Testing Feature Engineering")
    
    # Test 1: Small transaction
    print("\n1️⃣ Small Transaction ($50)")
    test1 = {
        "Time": 10000,
        "Amount": 50,
        "V1": 0.5, "V2": 0.3, "V3": -0.2, "V4": 0.8, "V5": 0.1,
        "V6": 0.4, "V7": -0.3, "V8": 0.2, "V9": 0.1, "V10": 0.3,
        "V11": 0.2, "V12": 0.1, "V13": -0.1, "V14": 0.4, "V15": 0.2,
        "V16": 0.3, "V17": -0.2, "V18": 0.1, "V19": 0.2, "V20": 0.1,
        "V21": 0.3, "V22": 0.2, "V23": 0.1, "V24": 0.2, "V25": 0.1,
        "V26": 0.2, "V27": 0.1, "V28": 0.1
    }
    debug_features(test1)
    
    # Test 2: Large transaction
    print("2️⃣ Large Transaction ($5000)")
    test2 = test1.copy()
    test2["Amount"] = 5000
    debug_features(test2)
    
    # Test 3: Very large transaction
    print("3️⃣ Very Large Transaction ($12500)")
    test3 = test1.copy()
    test3["Amount"] = 12500
    debug_features(test3)
    
    print("✅ Feature engineering test complete!")
    print("\nKey differences to check:")
    print("  - amount_roll_mean_3 should be DIFFERENT for each amount")
    print("  - amount_roll_std_3 should increase with amount size")