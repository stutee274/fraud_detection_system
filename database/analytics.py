# database/analytics.py - Analytics Functions for Phase 4
"""
Analytics module for fraud detection system
Provides functions to query and analyze prediction data
"""

from database.db import db, convert_decimals
from datetime import datetime, timedelta

# ============================================
# DAILY STATISTICS
# ============================================

def get_daily_fraud_stats(days=30):
    """
    Get daily fraud statistics
    
    Args:
        days: Number of days to look back (default 30)
        
    Returns:
        List of daily stats with:
        - date
        - total_transactions
        - fraud_detected
        - fraud_amount
        - avg_fraud_prob
        - fraud_rate
    """
    try:
        with db.get_cursor() as cursor:
            query = """
                SELECT 
                    DATE(predicted_at) as date,
                    COUNT(*) as total_transactions,
                    SUM(CASE WHEN prediction = 1 THEN 1 ELSE 0 END) as fraud_detected,
                    SUM(CASE WHEN prediction = 1 THEN amount ELSE 0 END) as fraud_amount,
                    AVG(fraud_probability) as avg_fraud_prob,
                    CASE 
                        WHEN COUNT(*) > 0 
                        THEN CAST(SUM(CASE WHEN prediction = 1 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*)
                        ELSE 0 
                    END as fraud_rate
                FROM predictions
                WHERE predicted_at >= CURRENT_DATE - INTERVAL '%s days'
                GROUP BY DATE(predicted_at)
                ORDER BY date DESC
            """
            cursor.execute(query, (days,))
            results = cursor.fetchall()
            
            return [convert_decimals(dict(r)) for r in results]
            
    except Exception as e:
        print(f"❌ Error fetching daily stats: {e}")
        return []


# ============================================
# MODEL PERFORMANCE
# ============================================

def get_model_performance_metrics():
    """
    Calculate model performance metrics from feedback
    
    Returns:
        Dict with:
        - total_predictions
        - total_feedback
        - accuracy
        - precision
        - recall
        - f1_score
        - true_positives
        - false_positives
        - true_negatives
        - false_negatives
    """
    try:
        with db.get_cursor() as cursor:
            # Get confusion matrix
            query = """
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN prediction = 1 AND actual_class = 1 THEN 1 ELSE 0 END) as tp,
                    SUM(CASE WHEN prediction = 1 AND actual_class = 0 THEN 1 ELSE 0 END) as fp,
                    SUM(CASE WHEN prediction = 0 AND actual_class = 1 THEN 1 ELSE 0 END) as fn,
                    SUM(CASE WHEN prediction = 0 AND actual_class = 0 THEN 1 ELSE 0 END) as tn
                FROM predictions
                WHERE actual_class IS NOT NULL
            """
            cursor.execute(query)
            result = cursor.fetchone()
            
            if not result or result['total'] == 0:
                return {
                    'status': 'insufficient_data',
                    'message': 'Not enough feedback to calculate metrics',
                    'total_predictions': 0,
                    'total_feedback': 0
                }
            
            tp = result['tp'] or 0
            fp = result['fp'] or 0
            fn = result['fn'] or 0
            tn = result['tn'] or 0
            total = result['total']
            
            # Calculate metrics
            accuracy = (tp + tn) / total if total > 0 else 0
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            
            # Get total predictions
            cursor.execute("SELECT COUNT(*) as count FROM predictions")
            total_predictions = cursor.fetchone()['count']
            
            return {
                'status': 'success',
                'total_predictions': total_predictions,
                'total_feedback': total,
                'feedback_rate': total / total_predictions if total_predictions > 0 else 0,
                'accuracy': round(accuracy, 4),
                'precision': round(precision, 4),
                'recall': round(recall, 4),
                'f1_score': round(f1_score, 4),
                'confusion_matrix': {
                    'true_positives': tp,
                    'false_positives': fp,
                    'true_negatives': tn,
                    'false_negatives': fn
                }
            }
            
    except Exception as e:
        print(f"❌ Error calculating performance metrics: {e}")
        return {'status': 'error', 'message': str(e)}


# ============================================
# FEEDBACK STATISTICS
# ============================================

def get_feedback_statistics():
    """
    Get feedback submission statistics
    
    Returns:
        Dict with feedback counts by type
    """
    try:
        with db.get_cursor() as cursor:
            query = """
                SELECT 
                    COUNT(*) as total_feedback,
                    SUM(CASE WHEN feedback_type = 'correct' THEN 1 ELSE 0 END) as correct,
                    SUM(CASE WHEN feedback_type = 'false_positive' THEN 1 ELSE 0 END) as false_positives,
                    SUM(CASE WHEN feedback_type = 'false_negative' THEN 1 ELSE 0 END) as false_negatives,
                    MIN(created_at) as first_feedback,
                    MAX(created_at) as last_feedback
                FROM feedback
            """
            cursor.execute(query)
            result = cursor.fetchone()
            
            if result:
                return convert_decimals(dict(result))
            return {}
            
    except Exception as e:
        print(f"❌ Error fetching feedback stats: {e}")
        return {}


# ============================================
# HOURLY TRENDS
# ============================================

def get_hourly_fraud_trends():
    """
    Get fraud detection rates by hour of day
    
    Returns:
        List of hourly stats (0-23)
    """
    try:
        with db.get_cursor() as cursor:
            query = """
                SELECT 
                    EXTRACT(HOUR FROM predicted_at) as hour,
                    COUNT(*) as total_transactions,
                    SUM(CASE WHEN prediction = 1 THEN 1 ELSE 0 END) as fraud_detected,
                    CASE 
                        WHEN COUNT(*) > 0 
                        THEN CAST(SUM(CASE WHEN prediction = 1 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*)
                        ELSE 0 
                    END as fraud_rate,
                    AVG(fraud_probability) as avg_fraud_prob
                FROM predictions
                WHERE predicted_at >= CURRENT_DATE - INTERVAL '7 days'
                GROUP BY EXTRACT(HOUR FROM predicted_at)
                ORDER BY hour
            """
            cursor.execute(query)
            results = cursor.fetchall()
            
            return [convert_decimals(dict(r)) for r in results]
            
    except Exception as e:
        print(f"❌ Error fetching hourly trends: {e}")
        return []


# ============================================
# AMOUNT ANALYSIS
# ============================================

def get_fraud_by_amount_range():
    """
    Analyze fraud detection by transaction amount ranges
    
    Returns:
        List of amount ranges with fraud stats
    """
    try:
        with db.get_cursor() as cursor:
            query = """
                WITH amount_ranges AS (
                    SELECT 
                        CASE 
                            WHEN amount < 50 THEN '0-50'
                            WHEN amount < 100 THEN '50-100'
                            WHEN amount < 500 THEN '100-500'
                            WHEN amount < 1000 THEN '500-1000'
                            WHEN amount < 5000 THEN '1000-5000'
                            ELSE '5000+'
                        END as amount_range,
                        prediction,
                        fraud_probability
                    FROM predictions
                )
                SELECT 
                    amount_range,
                    COUNT(*) as total_transactions,
                    SUM(CASE WHEN prediction = 1 THEN 1 ELSE 0 END) as fraud_detected,
                    AVG(fraud_probability) as avg_fraud_prob,
                    CASE 
                        WHEN COUNT(*) > 0 
                        THEN CAST(SUM(CASE WHEN prediction = 1 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*)
                        ELSE 0 
                    END as fraud_rate
                FROM amount_ranges
                GROUP BY amount_range
                ORDER BY 
                    CASE amount_range
                        WHEN '0-50' THEN 1
                        WHEN '50-100' THEN 2
                        WHEN '100-500' THEN 3
                        WHEN '500-1000' THEN 4
                        WHEN '1000-5000' THEN 5
                        ELSE 6
                    END
            """
            cursor.execute(query)
            results = cursor.fetchall()
            
            return [convert_decimals(dict(r)) for r in results]
            
    except Exception as e:
        print(f"❌ Error fetching amount analysis: {e}")
        return []


# ============================================
# TOP RISKY TRANSACTIONS
# ============================================

def get_top_risky_transactions(limit=10, days=7):
    """
    Get highest risk transactions (highest fraud probability)
    
    Args:
        limit: Number of transactions to return
        days: Look back period in days
        
    Returns:
        List of high-risk transactions
    """
    try:
        with db.get_cursor() as cursor:
            query = """
                SELECT 
                    id,
                    transaction_time,
                    amount,
                    prediction,
                    fraud_probability,
                    risk_level,
                    predicted_at,
                    actual_class
                FROM predictions
                WHERE predicted_at >= CURRENT_DATE - INTERVAL '%s days'
                ORDER BY fraud_probability DESC
                LIMIT %s
            """
            cursor.execute(query, (days, limit))
            results = cursor.fetchall()
            
            return [convert_decimals(dict(r)) for r in results]
            
    except Exception as e:
        print(f"❌ Error fetching risky transactions: {e}")
        return []


# ============================================
# COMPLETE DASHBOARD DATA
# ============================================

def get_dashboard_summary():
    """
    Get all analytics data for dashboard in one call
    
    Returns:
        Complete dashboard data including:
        - Overview stats
        - Daily trends
        - Model performance
        - Recent activity
    """
    try:
        with db.get_cursor() as cursor:
            # Overall stats
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_predictions,
                    SUM(CASE WHEN prediction = 1 THEN 1 ELSE 0 END) as total_fraud_detected,
                    SUM(CASE WHEN actual_class IS NOT NULL THEN 1 ELSE 0 END) as total_feedback,
                    AVG(fraud_probability) as avg_fraud_probability
                FROM predictions
            """)
            overview = cursor.fetchone()
            
            # Today's stats
            cursor.execute("""
                SELECT 
                    COUNT(*) as today_predictions,
                    SUM(CASE WHEN prediction = 1 THEN 1 ELSE 0 END) as today_fraud
                FROM predictions
                WHERE predicted_at >= CURRENT_DATE
            """)
            today = cursor.fetchone()
            
            # Last 24 hours
            cursor.execute("""
                SELECT 
                    COUNT(*) as last_24h_predictions,
                    SUM(CASE WHEN prediction = 1 THEN 1 ELSE 0 END) as last_24h_fraud
                FROM predictions
                WHERE predicted_at >= NOW() - INTERVAL '24 hours'
            """)
            last_24h = cursor.fetchone()
            
            return {
                'status': 'success',
                'generated_at': datetime.now().isoformat(),
                'overview': convert_decimals(dict(overview)) if overview else {},
                'today': convert_decimals(dict(today)) if today else {},
                'last_24_hours': convert_decimals(dict(last_24h)) if last_24h else {},
                'daily_trends': get_daily_fraud_stats(7),
                'model_performance': get_model_performance_metrics(),
                'feedback_stats': get_feedback_statistics(),
                'hourly_trends': get_hourly_fraud_trends(),
                'amount_analysis': get_fraud_by_amount_range(),
                'top_risky': get_top_risky_transactions(5, 7)
            }
            
    except Exception as e:
        print(f"❌ Error generating dashboard: {e}")
        return {'status': 'error', 'message': str(e)}


# ============================================
# RETRAINING READINESS CHECK
# ============================================

def check_retraining_readiness(min_feedback=100):
    """
    Check if enough feedback has been collected for retraining
    
    Args:
        min_feedback: Minimum feedback required (default 100)
        
    Returns:
        Dict with retraining status
    """
    try:
        with db.get_cursor() as cursor:
            # Count feedback
            cursor.execute("SELECT COUNT(*) as count FROM feedback")
            feedback_count = cursor.fetchone()['count']
            
            # Count by class
            cursor.execute("""
                SELECT 
                    actual_class,
                    COUNT(*) as count
                FROM predictions
                WHERE actual_class IS NOT NULL
                GROUP BY actual_class
            """)
            class_counts = cursor.fetchall()
            
            fraud_count = 0
            normal_count = 0
            for row in class_counts:
                if row['actual_class'] == 1:
                    fraud_count = row['count']
                else:
                    normal_count = row['count']
            
            ready = feedback_count >= min_feedback
            balanced = min(fraud_count, normal_count) >= 10  # Need at least 10 of each
            
            return {
                'status': 'success',
                'ready_for_retraining': ready and balanced,
                'feedback_count': feedback_count,
                'required_feedback': min_feedback,
                'fraud_feedback': fraud_count,
                'normal_feedback': normal_count,
                'is_balanced': balanced,
                'recommendation': 'Ready to retrain' if (ready and balanced) else f'Need {min_feedback - feedback_count} more feedback samples'
            }
            
    except Exception as e:
        print(f"❌ Error checking retraining readiness: {e}")
        return {'status': 'error', 'message': str(e)}


if __name__ == "__main__":
    # Test analytics functions
    from database.db import init_database
    
    print("🧪 Testing analytics functions...")
    init_database()
    
    print("\n1️⃣ Dashboard Summary:")
    dashboard = get_dashboard_summary()
    print(f"   Total Predictions: {dashboard['overview'].get('total_predictions', 0)}")
    print(f"   Total Fraud Detected: {dashboard['overview'].get('total_fraud_detected', 0)}")
    
    print("\n2️⃣ Model Performance:")
    performance = get_model_performance_metrics()
    if performance['status'] == 'success':
        print(f"   Accuracy: {performance['accuracy']}")
        print(f"   Precision: {performance['precision']}")
        print(f"   Recall: {performance['recall']}")
    
    print("\n3️⃣ Retraining Readiness:")
    readiness = check_retraining_readiness(100)
    print(f"   Ready: {readiness['ready_for_retraining']}")
    print(f"   Feedback Count: {readiness['feedback_count']}")
    
    print("\n✅ Analytics test complete!")