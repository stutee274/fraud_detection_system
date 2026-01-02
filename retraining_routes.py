# retraining_routes.py - PRODUCTION VERSION
"""
Retraining routes with flexible threshold for demo/production
"""

from flask import Blueprint, jsonify, request
from database.db_dual import db
import threading

# Import retraining functions
try:
    from retraining.auto_retrain_dual import (
        retrain_banking_with_dataset,
        retrain_credit_card_with_dataset
    )
    RETRAINING_AVAILABLE = True
except ImportError:
    RETRAINING_AVAILABLE = False
    print("⚠️  Auto-retraining not available")

# Configuration
RETRAIN_THRESHOLD = 50  # Lower threshold for demo (was 20)

# Global lock and tracking
_retraining_lock = threading.Lock()
_last_retrain_count = {'banking': 0, 'credit_card': 0}

def get_feedback_count(model_type=None):
    """Get count of predictions with feedback"""
    try:
        with db.get_cursor() as cursor:
            if model_type:
                cursor.execute("""
                    SELECT COUNT(*) as count 
                    FROM predictions 
                    WHERE actual_class IS NOT NULL AND model_type = %s
                """, (model_type,))
            else:
                cursor.execute("""
                    SELECT COUNT(*) as count 
                    FROM predictions 
                    WHERE actual_class IS NOT NULL
                """)
            
            result = cursor.fetchone()
            return result['count'] if result else 0
    except Exception as e:
        print(f"❌ Error getting feedback count: {e}")
        return 0

def auto_trigger_retraining():
    """Auto-trigger retraining when threshold reached"""
    global _last_retrain_count
    
    try:
        if not RETRAINING_AVAILABLE:
            return
        
        banking_count = get_feedback_count(model_type='banking')
        cc_count = get_feedback_count(model_type='credit_card')
        
        models_to_retrain = []
        
        # Check if threshold reached and not already retrained at this count
        if banking_count >= RETRAIN_THRESHOLD and _last_retrain_count['banking'] < RETRAIN_THRESHOLD:
            models_to_retrain.append('banking')
            _last_retrain_count['banking'] = banking_count
        
        if cc_count >= RETRAIN_THRESHOLD and _last_retrain_count['credit_card'] < RETRAIN_THRESHOLD:
            models_to_retrain.append('credit_card')
            _last_retrain_count['credit_card'] = cc_count
        
        if models_to_retrain and not _retraining_lock.locked():
            def background_retrain():
                with _retraining_lock:
                    for model in models_to_retrain:
                        try:
                            print(f"\n🎯 AUTO-RETRAINING {model.upper()} ({banking_count if model == 'banking' else cc_count} feedbacks)")
                            
                            if model == 'banking':
                                retrain_banking_with_dataset()
                            elif model == 'credit_card':
                                retrain_credit_card_with_dataset()
                                
                            print(f"✅ {model.upper()} retraining complete")
                        except Exception as e:
                            print(f"❌ {model} retraining error: {e}")
                            import traceback
                            traceback.print_exc()
            
            thread = threading.Thread(target=background_retrain, daemon=True, name=f"Retrain-{'-'.join(models_to_retrain)}")
            thread.start()
            print(f"✅ Started background retraining for: {', '.join(models_to_retrain)}")
    
    except Exception as e:
        print(f"❌ Auto-retraining check error: {e}")

def register_retraining_routes(app):
    """Register retraining routes"""
    
    @app.route("/api/retrain/status", methods=["GET"])
    def retrain_status():
        """Get retraining status"""
        try:
            banking_count = get_feedback_count(model_type='banking')
            cc_count = get_feedback_count(model_type='credit_card')
            
            return jsonify({
                'status': 'success',
                'threshold': RETRAIN_THRESHOLD,
                'banking': {
                    'feedback_count': banking_count,
                    'progress': f"{banking_count}/{RETRAIN_THRESHOLD}",
                    'ready': banking_count >= RETRAIN_THRESHOLD,
                    'percentage': round((banking_count / RETRAIN_THRESHOLD * 100) if RETRAIN_THRESHOLD > 0 else 0, 1)
                },
                'credit_card': {
                    'feedback_count': cc_count,
                    'progress': f"{cc_count}/{RETRAIN_THRESHOLD}",
                    'ready': cc_count >= RETRAIN_THRESHOLD,
                    'percentage': round((cc_count / RETRAIN_THRESHOLD * 100) if RETRAIN_THRESHOLD > 0 else 0, 1)
                },
                'retraining_available': RETRAINING_AVAILABLE,
                'currently_retraining': _retraining_lock.locked()
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    @app.route("/api/retrain/trigger", methods=["POST"])
    def trigger_retrain():
        """Manually trigger retraining"""
        try:
            if not RETRAINING_AVAILABLE:
                return jsonify({
                    'status': 'error',
                    'message': 'Retraining not available'
                }), 503
            
            if _retraining_lock.locked():
                return jsonify({
                    'status': 'error',
                    'message': 'Retraining already in progress'
                }), 409
            
            data = request.get_json() or {}
            model_type = data.get('model_type', 'both')
            
            def background_retrain():
                with _retraining_lock:
                    if model_type in ['banking', 'both']:
                        try:
                            print("\n🎯 MANUAL RETRAINING: BANKING")
                            retrain_banking_with_dataset()
                        except Exception as e:
                            print(f"❌ Banking retraining error: {e}")
                    
                    if model_type in ['credit_card', 'both']:
                        try:
                            print("\n🎯 MANUAL RETRAINING: CREDIT CARD")
                            retrain_credit_card_with_dataset()
                        except Exception as e:
                            print(f"❌ Credit card retraining error: {e}")
            
            thread = threading.Thread(target=background_retrain, daemon=True)
            thread.start()
            
            return jsonify({
                'status': 'success',
                'message': f'Retraining started for {model_type}'
            })
        
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    print("✅ Retraining routes registered")