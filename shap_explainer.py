# # shap_explainer.py - Robust SHAP explainer with proper error handling
# import shap
# import pandas as pd
# import numpy as np
# import warnings
# warnings.filterwarnings('ignore')

# class ShapExplainer:
#     """SHAP explainer for fraud detection model"""
    
#     def __init__(self, model, feature_names):
#         """
#         Initialize SHAP explainer
        
#         Args:
#             model: XGBClassifier model
#             feature_names: List of feature names
#         """
#         self.model = model
#         self.feature_names = feature_names
#         self.explainer = None
#         self.is_working = False
        
#         try:
#             print("   Initializing SHAP TreeExplainer...")
            
#             # Create sample data for explainer background
#             # This helps SHAP understand the feature space
#             sample_data = pd.DataFrame(
#                 np.zeros((100, len(feature_names))),
#                 columns=feature_names
#             )
            
#             # Initialize TreeExplainer
#             self.explainer = shap.TreeExplainer(model, sample_data)
            
#             # Test if it actually works
#             test_X = pd.DataFrame(
#                 [np.zeros(len(feature_names))],
#                 columns=feature_names
#             )
#             _ = self.explainer.shap_values(test_X)
            
#             self.is_working = True
#             print("   ✅ SHAP explainer initialized and tested successfully")
            
#         except Exception as e:
#             print(f"   ⚠️  SHAP initialization failed: {e}")
#             print("   Falling back to feature importance method")
#             self.explainer = None
#             self.is_working = False
            
#             # Fallback: use feature importance
#             try:
#                 self.feature_importances = model.feature_importances_
#             except:
#                 self.feature_importances = np.ones(len(feature_names)) / len(feature_names)
    
#     def explain(self, X, top_n=5):
#         """
#         Get top features contributing to prediction
        
#         Args:
#             X: DataFrame with features
#             top_n: Number of top features to return
            
#         Returns:
#             List of dicts with feature contributions
#         """
#         if not self.is_working or self.explainer is None:
#             # Fallback to feature importance method
#             return self._explain_with_importance(X, top_n)
        
#         try:
#             # Get SHAP values
#             shap_values = self.explainer.shap_values(X)
            
#             # Handle different SHAP value formats
#             if isinstance(shap_values, list):
#                 # Binary classification: use positive class (fraud)
#                 if len(shap_values) > 1:
#                     shap_vals = shap_values[1]
#                 else:
#                     shap_vals = shap_values[0]
#             else:
#                 shap_vals = shap_values
            
#             # Ensure it's 1D array for single prediction
#             if len(shap_vals.shape) > 1:
#                 shap_vals = shap_vals[0]
            
#             # Get absolute values for ranking
#             shap_abs = np.abs(shap_vals)
            
#             # Get top features
#             top_indices = np.argsort(shap_abs)[-top_n:][::-1]
            
#             top_features = []
#             for idx in top_indices:
#                 feature_name = self.feature_names[idx]
#                 contribution = float(shap_vals[idx])
#                 feature_value = float(X.iloc[0, idx])
                
#                 # Determine impact
#                 if contribution > 0:
#                     impact = "increases fraud risk"
#                 else:
#                     impact = "decreases fraud risk"
                
#                 top_features.append({
#                     "feature": feature_name,
#                     "value": round(feature_value, 4),
#                     "contribution": round(contribution, 4),
#                     "impact": impact
#                 })
            
#             return top_features
            
#         except Exception as e:
#             print(f"   ⚠️  SHAP explanation failed: {e}")
#             # Fallback to importance method
#             return self._explain_with_importance(X, top_n)
    
#     def _explain_with_importance(self, X, top_n=5):
#         """
#         Fallback explanation using feature importance
#         """
#         try:
#             feature_values = X.iloc[0].values
            
#             # Calculate contribution as: feature_value * feature_importance
#             contributions = feature_values * self.feature_importances
            
#             # Get prediction probability
#             proba = self.model.predict_proba(X)[0][1]
            
#             # Get top features by absolute contribution
#             top_indices = np.argsort(np.abs(contributions))[-top_n:][::-1]
            
#             top_features = []
#             for idx in top_indices:
#                 feature_name = self.feature_names[idx]
#                 feature_value = float(feature_values[idx])
#                 contribution = float(contributions[idx])
                
#                 # Determine impact based on contribution and prediction
#                 if contribution > 0:
#                     if proba > 0.5:
#                         impact = "increases fraud risk"
#                     else:
#                         impact = "suggests legitimate transaction"
#                 else:
#                     if proba > 0.5:
#                         impact = "partially offsets fraud indicators"
#                     else:
#                         impact = "decreases fraud risk"
                
#                 top_features.append({
#                     "feature": feature_name,
#                     "value": round(feature_value, 4),
#                     "contribution": round(contribution, 4),
#                     "impact": impact,
#                     "method": "feature_importance"
#                 })
            
#             return top_features
            
#         except Exception as e:
#             print(f"   ⚠️  Importance explanation also failed: {e}")
#             return []
    
#     def explain_detailed(self, X):
#         """
#         Get detailed SHAP explanation with all features
        
#         Returns:
#             Dict with base value, expected value, and all feature contributions
#         """
#         if not self.is_working or self.explainer is None:
#             return self._explain_detailed_with_importance(X)
        
#         try:
#             shap_values = self.explainer.shap_values(X)
            
#             if isinstance(shap_values, list):
#                 shap_vals = shap_values[1] if len(shap_values) > 1 else shap_values[0]
#             else:
#                 shap_vals = shap_values
            
#             if len(shap_vals.shape) > 1:
#                 shap_vals = shap_vals[0]
            
#             # Get expected value (base value)
#             expected_value = self.explainer.expected_value
#             if isinstance(expected_value, (list, np.ndarray)):
#                 expected_value = expected_value[1] if len(expected_value) > 1 else expected_value[0]
            
#             # Create detailed explanation
#             explanation = {
#                 "base_value": float(expected_value),
#                 "prediction": float(np.sum(shap_vals) + expected_value),
#                 "features": []
#             }
            
#             for idx, feature_name in enumerate(self.feature_names):
#                 explanation["features"].append({
#                     "name": feature_name,
#                     "value": float(X.iloc[0, idx]),
#                     "shap_value": float(shap_vals[idx])
#                 })
            
#             # Sort by absolute SHAP value
#             explanation["features"].sort(key=lambda x: abs(x["shap_value"]), reverse=True)
            
#             return explanation
            
#         except Exception as e:
#             print(f"   ⚠️  Detailed SHAP explanation failed: {e}")
#             return self._explain_detailed_with_importance(X)
    
#     def _explain_detailed_with_importance(self, X):
#         """
#         Fallback detailed explanation using feature importance
#         """
#         try:
#             feature_values = X.iloc[0].values
#             contributions = feature_values * self.feature_importances
#             proba = self.model.predict_proba(X)[0][1]
            
#             explanation = {
#                 "base_value": 0.5,
#                 "prediction": float(proba),
#                 "features": [],
#                 "method": "feature_importance"
#             }
            
#             for idx, feature_name in enumerate(self.feature_names):
#                 explanation["features"].append({
#                     "name": feature_name,
#                     "value": float(feature_values[idx]),
#                     "shap_value": float(contributions[idx]),  # Use 'shap_value' for consistency
#                     "importance": float(self.feature_importances[idx])
#                 })
            
#             # Sort by absolute shap_value
#             explanation["features"].sort(
#                 key=lambda x: abs(x["shap_value"]), 
#                 reverse=True
#             )
            
#             return explanation
            
#         except Exception as e:
#             print(f"   ⚠️  Detailed explanation failed: {e}")
#             return None



#### dual for both roles #####
# shap_explainer_dual.py - SHAP explainer for both Credit Card and Banking models
import shap
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

class DualShapExplainer:
    """Unified SHAP explainer for Credit Card and Banking fraud detection"""
    
    def __init__(self, model, feature_names, model_type="banking"):
        """
        Initialize SHAP explainer
        
        Args:
            model: Trained model (XGBoost or RandomForest)
            feature_names: List of feature names
            model_type: "credit_card" or "banking"
        """
        self.model = model
        self.feature_names = feature_names
        self.model_type = model_type
        self.explainer = None
        self.is_working = False
        
        try:
            print(f"   Initializing SHAP for {model_type} model...")
            
            # Create background data
            sample_data = pd.DataFrame(
                np.zeros((100, len(feature_names))),
                columns=feature_names
            )
            
            # Initialize TreeExplainer
            self.explainer = shap.TreeExplainer(model)
            
            # Test it
            test_X = pd.DataFrame(
                [np.zeros(len(feature_names))],
                columns=feature_names
            )
            _ = self.explainer.shap_values(test_X)
            
            self.is_working = True
            print(f"   ✅ SHAP explainer ready for {model_type}")
            
        except Exception as e:
            print(f"   ⚠️  SHAP initialization failed: {e}")
            print(f"   Using feature importance fallback")
            self.explainer = None
            self.is_working = False
            
            try:
                self.feature_importances = model.feature_importances_
            except:
                self.feature_importances = np.ones(len(feature_names)) / len(feature_names)
    
    def explain(self, X, top_n=5):
        """
        Get top features - GUARANTEED to return features
        
        Returns:
            List of dicts with feature contributions
        """
        # Try SHAP first
        if self.is_working and self.explainer is not None:
            try:
                shap_values = self.explainer.shap_values(X)
                
                # Handle different formats
                if isinstance(shap_values, list):
                    shap_vals = shap_values[1] if len(shap_values) > 1 else shap_values[0]
                else:
                    shap_vals = shap_values
                
                # Convert to numpy array if needed
                if not isinstance(shap_vals, np.ndarray):
                    shap_vals = np.array(shap_vals)
                
                # Flatten if needed
                if len(shap_vals.shape) > 1:
                    shap_vals = shap_vals.flatten()
                
                # Ensure correct length
                if len(shap_vals) != len(self.feature_names):
                    print(f"   ⚠️  SHAP length mismatch: {len(shap_vals)} vs {len(self.feature_names)}")
                    raise ValueError("Length mismatch")
                
                # Get top features
                shap_abs = np.abs(shap_vals)
                top_indices = np.argsort(shap_abs)[-top_n:][::-1]
                
                top_features = []
                for idx in top_indices:
                    feature_name = self.feature_names[idx]
                    shap_value = float(shap_vals[idx])
                    
                    # Get feature value safely
                    if hasattr(X, 'iloc'):
                        feature_value = float(X.iloc[0, idx])
                    elif hasattr(X, '__getitem__'):
                        feature_value = float(X[0][idx])
                    else:
                        feature_value = 0.0
                    
                    impact = "increases" if shap_value > 0 else "decreases"
                    
                    top_features.append({
                        "feature": feature_name,
                        "value": round(feature_value, 4),
                        "shap_value": round(shap_value, 4),
                        "impact": impact
                    })
                
                if len(top_features) > 0:
                    return top_features
                else:
                    print(f"   ⚠️  SHAP returned empty, using fallback")
                    
            except Exception as e:
                print(f"   ⚠️  SHAP error: {e}, using fallback")
        
        # ALWAYS use fallback if SHAP failed
        return self._explain_with_importance(X, top_n)
    
    def _explain_with_importance(self, X, top_n=5):
        """Fallback using feature importance - GUARANTEED to work"""
        try:
            # Get feature values
            if hasattr(X, 'iloc'):
                feature_values = X.iloc[0].values
            elif hasattr(X, 'values'):
                feature_values = X.values[0]
            else:
                feature_values = np.array(X[0])
            
            # Ensure we have importance values
            if not hasattr(self, 'feature_importances') or self.feature_importances is None:
                try:
                    self.feature_importances = self.model.feature_importances_
                except:
                    # Last resort: equal importance
                    self.feature_importances = np.ones(len(self.feature_names)) / len(self.feature_names)
            
            # Calculate contributions
            contributions = feature_values * self.feature_importances
            
            # Get top features
            top_indices = np.argsort(np.abs(contributions))[-top_n:][::-1]
            
            top_features = []
            for idx in top_indices:
                feature_name = self.feature_names[idx]
                feature_value = float(feature_values[idx])
                contribution = float(contributions[idx])
                
                impact = "increases" if contribution > 0 else "decreases"
                
                top_features.append({
                    "feature": feature_name,
                    "value": round(feature_value, 4),
                    "shap_value": round(contribution, 4),
                    "impact": impact,
                    "method": "importance"
                })
            
            return top_features
            
        except Exception as e:
            print(f"   ❌ Fallback FAILED: {e}")
            # Absolute last resort: return top features with zero contribution
            return [
                {
                    "feature": self.feature_names[i],
                    "value": 0.0,
                    "shap_value": 0.0,
                    "impact": "unknown",
                    "method": "error"
                }
                for i in range(min(top_n, len(self.feature_names)))
            ]


if __name__ == "__main__":
    print("SHAP Explainer module loaded")