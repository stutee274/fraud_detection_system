# # analytics_routes.py - Analytics API endpoints for Flask
# """
# Analytics routes for fraud detection API
# Add these routes to your app_db.py
# """

# from flask import jsonify, request
# from database.analytics import (
#     get_daily_fraud_stats,
#     get_model_performance_metrics,
#     get_feedback_statistics,
#     get_hourly_fraud_trends,
#     get_fraud_by_amount_range,
#     get_top_risky_transactions,
#     get_dashboard_summary,
#     check_retraining_readiness
# )

# # ============================================
# # ANALYTICS ROUTES
# # ============================================

# def register_analytics_routes(app):
#     """Register all analytics routes with Flask app"""
    
#     @app.route("/api/analytics/daily", methods=["GET"])
#     def analytics_daily():
#         """Get daily fraud statistics"""
#         try:
#             days = request.args.get('days', 30, type=int)
#             stats = get_daily_fraud_stats(days)
            
#             return jsonify({
#                 "status": "success",
#                 "days": days,
#                 "data": stats
#             })
#         except Exception as e:
#             return jsonify({
#                 "status": "error",
#                 "message": str(e)
#             }), 500
    
    
#     @app.route("/api/analytics/performance", methods=["GET"])
#     def analytics_performance():
#         """Get model performance metrics"""
#         try:
#             metrics = get_model_performance_metrics()
#             return jsonify(metrics)
#         except Exception as e:
#             return jsonify({
#                 "status": "error",
#                 "message": str(e)
#             }), 500
    
    
#     @app.route("/api/analytics/feedback", methods=["GET"])
#     def analytics_feedback():
#         """Get feedback statistics"""
#         try:
#             stats = get_feedback_statistics()
            
#             return jsonify({
#                 "status": "success",
#                 "data": stats
#             })
#         except Exception as e:
#             return jsonify({
#                 "status": "error",
#                 "message": str(e)
#             }), 500
    
    
#     @app.route("/api/analytics/hourly", methods=["GET"])
#     def analytics_hourly():
#         """Get hourly fraud trends"""
#         try:
#             trends = get_hourly_fraud_trends()
            
#             return jsonify({
#                 "status": "success",
#                 "data": trends
#             })
#         except Exception as e:
#             return jsonify({
#                 "status": "error",
#                 "message": str(e)
#             }), 500
    
    
#     @app.route("/api/analytics/amounts", methods=["GET"])
#     def analytics_amounts():
#         """Get fraud analysis by amount ranges"""
#         try:
#             analysis = get_fraud_by_amount_range()
            
#             return jsonify({
#                 "status": "success",
#                 "data": analysis
#             })
#         except Exception as e:
#             return jsonify({
#                 "status": "error",
#                 "message": str(e)
#             }), 500
    
    
#     @app.route("/api/analytics/risky", methods=["GET"])
#     def analytics_risky():
#         """Get top risky transactions"""
#         try:
#             limit = request.args.get('limit', 10, type=int)
#             days = request.args.get('days', 7, type=int)
            
#             transactions = get_top_risky_transactions(limit, days)
            
#             return jsonify({
#                 "status": "success",
#                 "limit": limit,
#                 "days": days,
#                 "data": transactions
#             })
#         except Exception as e:
#             return jsonify({
#                 "status": "error",
#                 "message": str(e)
#             }), 500
    
    
#     @app.route("/api/analytics/dashboard", methods=["GET"])
#     def analytics_dashboard():
#         """Get complete dashboard data"""
#         try:
#             dashboard = get_dashboard_summary()
#             return jsonify(dashboard)
#         except Exception as e:
#             return jsonify({
#                 "status": "error",
#                 "message": str(e)
#             }), 500
    
    
#     @app.route("/api/analytics/retraining-status", methods=["GET"])
#     def analytics_retraining_status():
#         """Check if model is ready for retraining"""
#         try:
#             min_feedback = request.args.get('min_feedback', 100, type=int)
#             status = check_retraining_readiness(min_feedback)
            
#             return jsonify(status)
#         except Exception as e:
#             return jsonify({
#                 "status": "error",
#                 "message": str(e)
#             }), 500
    
    
#     print("✅ Analytics routes registered")
#     print("   - GET /api/analytics/daily")
#     print("   - GET /api/analytics/performance")
#     print("   - GET /api/analytics/feedback")
#     print("   - GET /api/analytics/hourly")
#     print("   - GET /api/analytics/amounts")
#     print("   - GET /api/analytics/risky")
#     print("   - GET /api/analytics/dashboard")
#     print("   - GET /api/analytics/retraining-status")


### dual mode 
# analytics_routes.py - Phase 4: Analytics Dashboard
"""
Analytics endpoints for fraud detection system
- Daily statistics
- Model performance metrics
- Fraud trends
- High-risk transactions
"""

from flask import jsonify, request
from database.db_dual import (
    get_daily_stats,
    get_model_performance,
    get_recent_predictions,
    get_feedback_count,
    db
)

def register_analytics_routes(app):
    """Register all analytics routes"""
    
    @app.route("/api/analytics/dashboard", methods=["GET"])
    def analytics_dashboard():
        """Get complete dashboard statistics"""
        try:
            with db.get_cursor() as cursor:
                # Total predictions
                cursor.execute("SELECT COUNT(*) as count FROM predictions")
                total_predictions = cursor.fetchone()['count']
                
                # Total fraud detected
                cursor.execute("SELECT COUNT(*) as count FROM predictions WHERE prediction = 1")
                total_fraud = cursor.fetchone()['count']
                
                # Fraud rate
                fraud_rate = (total_fraud / total_predictions * 100) if total_predictions > 0 else 0
                
                # Today's stats
                cursor.execute("""
                    SELECT 
                        COUNT(*) as count,
                        SUM(CASE WHEN prediction = 1 THEN 1 ELSE 0 END) as fraud_count
                    FROM predictions
                    WHERE predicted_at::date = CURRENT_DATE
                """)
                today = cursor.fetchone()
                
                # By model type
                cursor.execute("""
                    SELECT 
                        model_type,
                        COUNT(*) as count,
                        SUM(CASE WHEN prediction = 1 THEN 1 ELSE 0 END) as fraud_count,
                        AVG(fraud_probability) as avg_probability
                    FROM predictions
                    GROUP BY model_type
                """)
                by_model = cursor.fetchall()
                
                # Feedback stats
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_feedback,
                        SUM(CASE WHEN prediction = actual_class THEN 1 ELSE 0 END) as correct_predictions
                    FROM predictions
                    WHERE actual_class IS NOT NULL
                """)
                feedback_stats = cursor.fetchone()
                
                accuracy = 0
                if feedback_stats and feedback_stats['total_feedback'] > 0:
                    accuracy = (feedback_stats['correct_predictions'] / feedback_stats['total_feedback']) * 100
                
                return jsonify({
                    "status": "success",
                    "dashboard": {
                        "total_predictions": total_predictions,
                        "total_fraud_detected": total_fraud,
                        "fraud_rate": round(fraud_rate, 2),
                        "today": {
                            "predictions": today['count'] if today else 0,
                            "fraud_detected": today['fraud_count'] if today else 0
                        },
                        "by_model": [dict(m) for m in by_model],
                        "feedback": {
                            "total": feedback_stats['total_feedback'] if feedback_stats else 0,
                            "correct": feedback_stats['correct_predictions'] if feedback_stats else 0,
                            "accuracy": round(accuracy, 2)
                        }
                    }
                })
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    
    @app.route("/api/analytics/daily-stats", methods=["GET"])
    def get_daily_statistics():
        """Get daily statistics"""
        try:
            days = request.args.get('days', 7, type=int)
            model_type = request.args.get('model_type', None)
            
            stats = get_daily_stats(days, model_type)
            
            return jsonify({
                "status": "success",
                "days": days,
                "model_type": model_type,
                "stats": stats
            })
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    
    @app.route("/api/analytics/model-performance", methods=["GET"])
    def model_performance_stats():
        """Get model performance metrics"""
        try:
            performance = get_model_performance()
            
            return jsonify({
                "status": "success",
                "performance": performance
            })
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    
    print("✅ Analytics routes registered")