
# ###-------------------------------------------------------

# #---------------------------------------------------------


# ###############  UPDATED AND FIXED ###############################


# # # database/db.py - Fixed Database Connection Module for Flask
# # import psycopg2
# # from psycopg2 import pool
# # from psycopg2.extras import RealDictCursor
# # import os
# # from contextlib import contextmanager
# # import json

# # # ============================================
# # # DATABASE CONNECTION CONFIGURATION
# # # ============================================

# # class Database:
# #     """Database connection manager"""
    
# #     def __init__(self):
# #         self.connection_pool = None
# #         self.config = {
# #             'host': os.getenv('DB_HOST', 'localhost'),
# #             'port': os.getenv('DB_PORT', '5432'),
# #             'database': os.getenv('DB_NAME', 'fraud_detection'),
# #             'user': os.getenv('DB_USER', 'postgres'),
# #             'password': os.getenv('DB_PASSWORD', 'your_password_here')
# #         }
    
# #     def initialize_pool(self, minconn=1, maxconn=10):
# #         """Initialize connection pool"""
# #         try:
# #             # Close existing pool if any
# #             if self.connection_pool is not None:
# #                 try:
# #                     self.connection_pool.closeall()
# #                 except:
# #                     pass
            
# #             self.connection_pool = psycopg2.pool.SimpleConnectionPool(
# #                 minconn,
# #                 maxconn,
# #                 **self.config
# #             )
# #             print("✅ Database connection pool created")
# #             return True
# #         except Exception as e:
# #             print(f"❌ Error creating connection pool: {e}")
# #             return False
    
# #     def ensure_pool(self):
# #         """Ensure connection pool exists (for Flask debug mode)"""
# #         if self.connection_pool is None or self.connection_pool.closed:
# #             self.initialize_pool()
    
# #     @contextmanager
# #     def get_connection(self):
# #         """Get connection from pool (context manager)"""
# #         self.ensure_pool()  # Make sure pool exists
# #         conn = None
# #         try:
# #             conn = self.connection_pool.getconn()
# #             yield conn
# #         finally:
# #             if conn:
# #                 self.connection_pool.putconn(conn)
    
# #     @contextmanager
# #     def get_cursor(self, cursor_factory=RealDictCursor):
# #         """Get cursor (context manager)"""
# #         with self.get_connection() as conn:
# #             cursor = conn.cursor(cursor_factory=cursor_factory)
# #             try:
# #                 yield cursor
# #                 conn.commit()
# #             except Exception as e:
# #                 conn.rollback()
# #                 raise e
# #             finally:
# #                 cursor.close()
    
# #     def close_all_connections(self):
# #         """Close all connections in pool"""
# #         if self.connection_pool and not self.connection_pool.closed:
# #             try:
# #                 self.connection_pool.closeall()
# #                 print("✅ All database connections closed")
# #             except Exception as e:
# #                 print(f"⚠️  Error closing connections: {e}")


# # # Global database instance
# # db = Database()


# # # ============================================
# # # DATABASE OPERATIONS
# # # ============================================

# # def save_prediction(prediction_data):
# #     """
# #     Save prediction to database
    
# #     Args:
# #         prediction_data: Dict with prediction details
        
# #     Returns:
# #         prediction_id (int) or None if error
# #     """
# #     try:
# #         with db.get_cursor() as cursor:
# #             # Prepare data
# #             top_features_json = json.dumps(prediction_data.get('top_features', []))
            
# #             query = """
# #                 INSERT INTO predictions (
# #                     transaction_time, amount,
# #                     v1, v2, v3, v4, v5, v6, v7, v8, v9, v10,
# #                     v11, v12, v13, v14, v15, v16, v17, v18, v19, v20,
# #                     v21, v22, v23, v24, v25, v26, v27, v28,
# #                     prediction, fraud_probability, risk_level, threshold_used,
# #                     top_features, ai_explanation, ai_provider,
# #                     model_version_id, api_endpoint, request_ip
# #                 ) VALUES (
# #                     %(transaction_time)s, %(amount)s,
# #                     %(v1)s, %(v2)s, %(v3)s, %(v4)s, %(v5)s, %(v6)s, %(v7)s, %(v8)s, %(v9)s, %(v10)s,
# #                     %(v11)s, %(v12)s, %(v13)s, %(v14)s, %(v15)s, %(v16)s, %(v17)s, %(v18)s, %(v19)s, %(v20)s,
# #                     %(v21)s, %(v22)s, %(v23)s, %(v24)s, %(v25)s, %(v26)s, %(v27)s, %(v28)s,
# #                     %(prediction)s, %(fraud_probability)s, %(risk_level)s, %(threshold_used)s,
# #                     %(top_features)s::jsonb, %(ai_explanation)s, %(ai_provider)s,
# #                     (SELECT id FROM model_versions WHERE is_active = TRUE LIMIT 1),
# #                     %(api_endpoint)s, %(request_ip)s
# #                 ) RETURNING id
# #             """
            
# #             # Add top_features as JSON string
# #             prediction_data['top_features'] = top_features_json
            
# #             cursor.execute(query, prediction_data)
# #             prediction_id = cursor.fetchone()['id']
            
# #             return prediction_id
            
# #     except Exception as e:
# #         print(f"❌ Error saving prediction: {e}")
# #         return None


# # def get_prediction_by_id(prediction_id):
# #     """Get prediction by ID"""
# #     try:
# #         with db.get_cursor() as cursor:
# #             query = """
# #                 SELECT 
# #                     p.*,
# #                     mv.version as model_version,
# #                     mv.threshold as model_threshold
# #                 FROM predictions p
# #                 LEFT JOIN model_versions mv ON p.model_version_id = mv.id
# #                 WHERE p.id = %s
# #             """
# #             cursor.execute(query, (prediction_id,))
# #             return cursor.fetchone()
# #     except Exception as e:
# #         print(f"❌ Error fetching prediction: {e}")
# #         return None


# # def get_recent_predictions(limit=50):
# #     """Get recent predictions"""
# #     try:
# #         with db.get_cursor() as cursor:
# #             query = """
# #                 SELECT 
# #                     id, amount, prediction, fraud_probability,
# #                     risk_level, predicted_at
# #                 FROM predictions
# #                 ORDER BY predicted_at DESC
# #                 LIMIT %s
# #             """
# #             cursor.execute(query, (limit,))
# #             return cursor.fetchall()
# #     except Exception as e:
# #         print(f"❌ Error fetching predictions: {e}")
# #         return []


# # def update_prediction_feedback(prediction_id, actual_class, feedback_note=None):
# #     """Update prediction with actual label (feedback)"""
# #     try:
# #         with db.get_cursor() as cursor:
# #             # Update predictions table
# #             cursor.execute("""
# #                 UPDATE predictions
# #                 SET actual_class = %s, feedback_received_at = CURRENT_TIMESTAMP
# #                 WHERE id = %s
# #             """, (actual_class, prediction_id))
            
# #             # Determine feedback type
# #             cursor.execute("""
# #                 SELECT prediction, actual_class
# #                 FROM predictions
# #                 WHERE id = %s
# #             """, (prediction_id,))
            
# #             result = cursor.fetchone()
# #             if result:
# #                 pred = result['prediction']
# #                 actual = result['actual_class']
                
# #                 if pred == actual:
# #                     feedback_type = "correct"
# #                 elif pred == 1 and actual == 0:
# #                     feedback_type = "false_positive"
# #                 else:
# #                     feedback_type = "false_negative"
                
# #                 # Insert into feedback table
# #                 cursor.execute("""
# #                     INSERT INTO feedback (
# #                         prediction_id, actual_class, feedback_type, feedback_note
# #                     ) VALUES (%s, %s, %s, %s)
# #                 """, (prediction_id, actual_class, feedback_type, feedback_note))
            
# #             return True
            
# #     except Exception as e:
# #         print(f"❌ Error updating feedback: {e}")
# #         return False


# # def get_daily_stats():
# #     """Get daily fraud statistics"""
# #     try:
# #         with db.get_cursor() as cursor:
# #             cursor.execute("SELECT * FROM daily_fraud_stats LIMIT 30")
# #             return cursor.fetchall()
# #     except Exception as e:
# #         print(f"❌ Error fetching daily stats: {e}")
# #         return []


# # def get_model_performance():
# #     """Get model performance metrics"""
# #     try:
# #         with db.get_cursor() as cursor:
# #             cursor.execute("SELECT * FROM model_performance")
# #             return cursor.fetchall()
# #     except Exception as e:
# #         print(f"❌ Error fetching model performance: {e}")
# #         return []


# # # ============================================
# # # INITIALIZATION
# # # ============================================

# # def init_database():
# #     """Initialize database connection"""
# #     success = db.initialize_pool()
# #     if success:
# #         print("✅ Database initialized successfully")
# #     else:
# #         print("⚠️  Database initialization failed - app will run without DB")
# #     return success


# # def close_database():
# #     """Close database connections"""
# #     db.close_all_connections()


# # # ============================================
# # # TESTING
# # # ============================================

# # if __name__ == "__main__":
# #     print("🧪 Testing database connection...")
    
# #     # Initialize
# #     if init_database():
# #         print("✅ Connection successful")
        
# #         # Test query
# #         try:
# #             with db.get_cursor() as cursor:
# #                 cursor.execute("SELECT version FROM model_versions WHERE is_active = TRUE")
# #                 result = cursor.fetchone()
# #                 if result:
# #                     print(f"✅ Active model version: {result['version']}")
# #                 else:
# #                     print("⚠️  No active model found")
# #         except Exception as e:
# #             print(f"❌ Test query failed: {e}")
        
# #         # Close
# #         close_database()
# #     else:
# #         print("❌ Connection failed")




#     ##########################################
#     ##.......................................................................................


#     # database/db.py - COMPLETE FIXED VERSION
# import psycopg2
# from psycopg2 import pool
# from psycopg2.extras import RealDictCursor
# import os
# from contextlib import contextmanager
# import json
# from decimal import Decimal

# # ============================================
# # HELPER FUNCTIONS
# # ============================================

# def convert_decimals(obj):
#     """
#     Convert Decimal objects to float for JSON serialization
#     Recursively handles nested dicts and lists
#     """
#     if isinstance(obj, dict):
#         return {k: convert_decimals(v) for k, v in obj.items()}
#     elif isinstance(obj, list):
#         return [convert_decimals(item) for item in obj]
#     elif isinstance(obj, Decimal):
#         return float(obj)
#     else:
#         return obj


# # ============================================
# # DATABASE CONNECTION CONFIGURATION
# # ============================================

# class Database:
#     """Database connection manager with Flask debug mode support"""
    
#     def __init__(self):
#         self.connection_pool = None
#         self.config = {
#             'host': os.getenv('DB_HOST', 'localhost'),
#             'port': os.getenv('DB_PORT', '5432'),
#             'database': os.getenv('DB_NAME', 'fraud_detection'),
#             'user': os.getenv('DB_USER', 'postgres'),
#             'password': os.getenv('DB_PASSWORD', 'your_password_here')
#         }
    
#     def initialize_pool(self, minconn=1, maxconn=10):
#         """Initialize connection pool"""
#         try:
#             # Close existing pool if any
#             if self.connection_pool is not None:
#                 try:
#                     self.connection_pool.closeall()
#                 except:
#                     pass
            
#             self.connection_pool = psycopg2.pool.SimpleConnectionPool(
#                 minconn,
#                 maxconn,
#                 **self.config
#             )
#             print("✅ Database connection pool created")
#             return True
#         except Exception as e:
#             print(f"❌ Error creating connection pool: {e}")
#             return False
    
#     def ensure_pool(self):
#         """Ensure connection pool exists (for Flask debug mode auto-reload)"""
#         if self.connection_pool is None or self.connection_pool.closed:
#             self.initialize_pool()
    
#     @contextmanager
#     def get_connection(self):
#         """Get connection from pool (context manager)"""
#         self.ensure_pool()  # Make sure pool exists
#         conn = None
#         try:
#             conn = self.connection_pool.getconn()
#             yield conn
#         finally:
#             if conn:
#                 self.connection_pool.putconn(conn)
    
#     @contextmanager
#     def get_cursor(self, cursor_factory=RealDictCursor):
#         """Get cursor (context manager)"""
#         with self.get_connection() as conn:
#             cursor = conn.cursor(cursor_factory=cursor_factory)
#             try:
#                 yield cursor
#                 conn.commit()
#             except Exception as e:
#                 conn.rollback()
#                 raise e
#             finally:
#                 cursor.close()
    
#     def close_all_connections(self):
#         """Close all connections in pool"""
#         if self.connection_pool and not self.connection_pool.closed:
#             try:
#                 self.connection_pool.closeall()
#                 print("✅ All database connections closed")
#             except Exception as e:
#                 print(f"⚠️  Error closing connections: {e}")


# # Global database instance
# db = Database()


# # ============================================
# # DATABASE OPERATIONS
# # ============================================

# def save_prediction(prediction_data):
#     """
#     Save prediction to database
    
#     Args:
#         prediction_data: Dict with prediction details
        
#     Returns:
#         prediction_id (int) or None if error
#     """
#     try:
#         with db.get_cursor() as cursor:
#             # Prepare data
#             top_features_json = json.dumps(prediction_data.get('top_features', []))
            
#             query = """
#                 INSERT INTO predictions (
#                     transaction_time, amount,
#                     v1, v2, v3, v4, v5, v6, v7, v8, v9, v10,
#                     v11, v12, v13, v14, v15, v16, v17, v18, v19, v20,
#                     v21, v22, v23, v24, v25, v26, v27, v28,
#                     prediction, fraud_probability, risk_level, threshold_used,
#                     top_features, ai_explanation, ai_provider,
#                     model_version_id, api_endpoint, request_ip
#                 ) VALUES (
#                     %(transaction_time)s, %(amount)s,
#                     %(v1)s, %(v2)s, %(v3)s, %(v4)s, %(v5)s, %(v6)s, %(v7)s, %(v8)s, %(v9)s, %(v10)s,
#                     %(v11)s, %(v12)s, %(v13)s, %(v14)s, %(v15)s, %(v16)s, %(v17)s, %(v18)s, %(v19)s, %(v20)s,
#                     %(v21)s, %(v22)s, %(v23)s, %(v24)s, %(v25)s, %(v26)s, %(v27)s, %(v28)s,
#                     %(prediction)s, %(fraud_probability)s, %(risk_level)s, %(threshold_used)s,
#                     %(top_features)s::jsonb, %(ai_explanation)s, %(ai_provider)s,
#                     (SELECT id FROM model_versions WHERE is_active = TRUE LIMIT 1),
#                     %(api_endpoint)s, %(request_ip)s
#                 ) RETURNING id
#             """
            
#             # Add top_features as JSON string
#             prediction_data['top_features'] = top_features_json
            
#             cursor.execute(query, prediction_data)
#             prediction_id = cursor.fetchone()['id']
            
#             return prediction_id
            
#     except Exception as e:
#         print(f"❌ Error saving prediction: {e}")
#         return None


# def get_prediction_by_id(prediction_id):
#     """Get prediction by ID with proper type conversion"""
#     try:
#         with db.get_cursor() as cursor:
#             query = """
#                 SELECT 
#                     p.*,
#                     mv.version as model_version,
#                     mv.threshold as model_threshold
#                 FROM predictions p
#                 LEFT JOIN model_versions mv ON p.model_version_id = mv.id
#                 WHERE p.id = %s
#             """
#             cursor.execute(query, (prediction_id,))
#             result = cursor.fetchone()
            
#             if result:
#                 # Convert to dict and handle Decimals
#                 result_dict = dict(result)
#                 return convert_decimals(result_dict)
#             return None
            
#     except Exception as e:
#         print(f"❌ Error fetching prediction: {e}")
#         return None


# def get_recent_predictions(limit=50):
#     """Get recent predictions with proper type conversion"""
#     try:
#         with db.get_cursor() as cursor:
#             query = """
#                 SELECT 
#                     id, amount, prediction, fraud_probability,
#                     risk_level, predicted_at
#                 FROM predictions
#                 ORDER BY predicted_at DESC
#                 LIMIT %s
#             """
#             cursor.execute(query, (limit,))
#             results = cursor.fetchall()
            
#             # Convert all results
#             converted_results = []
#             for result in results:
#                 result_dict = dict(result)
#                 converted_results.append(convert_decimals(result_dict))
            
#             return converted_results
            
#     except Exception as e:
#         print(f"❌ Error fetching predictions: {e}")
#         return []


# def update_prediction_feedback(prediction_id, actual_class, feedback_note=None):
#     """Update prediction with actual label (feedback)"""
#     try:
#         with db.get_cursor() as cursor:
#             # Update predictions table
#             cursor.execute("""
#                 UPDATE predictions
#                 SET actual_class = %s, feedback_received_at = CURRENT_TIMESTAMP
#                 WHERE id = %s
#             """, (actual_class, prediction_id))
            
#             # Determine feedback type
#             cursor.execute("""
#                 SELECT prediction, actual_class
#                 FROM predictions
#                 WHERE id = %s
#             """, (prediction_id,))
            
#             result = cursor.fetchone()
#             if result:
#                 pred = result['prediction']
#                 actual = result['actual_class']
                
#                 if pred == actual:
#                     feedback_type = "correct"
#                 elif pred == 1 and actual == 0:
#                     feedback_type = "false_positive"
#                 else:
#                     feedback_type = "false_negative"
                
#                 # Insert into feedback table
#                 cursor.execute("""
#                     INSERT INTO feedback (
#                         prediction_id, actual_class, feedback_type, feedback_note
#                     ) VALUES (%s, %s, %s, %s)
#                 """, (prediction_id, actual_class, feedback_type, feedback_note))
            
#             return True
            
#     except Exception as e:
#         print(f"❌ Error updating feedback: {e}")
#         return False


# def get_feedback_count():
#     """Get total number of feedback submissions"""
#     try:
#         with db.get_cursor() as cursor:
#             cursor.execute("SELECT COUNT(*) as count FROM feedback")
#             result = cursor.fetchone()
#             return result['count'] if result else 0
#     except Exception as e:
#         print(f"❌ Error getting feedback count: {e}")
#         return 0


# def get_feedback_for_retraining(limit=None):
#     """
#     Get feedback data for model retraining
#     Returns: List of dicts with transaction features and actual labels
#     """
#     try:
#         with db.get_cursor() as cursor:
#             query = """
#                 SELECT 
#                     p.transaction_time as Time,
#                     p.amount as Amount,
#                     p.v1 as V1, p.v2 as V2, p.v3 as V3, p.v4 as V4, p.v5 as V5,
#                     p.v6 as V6, p.v7 as V7, p.v8 as V8, p.v9 as V9, p.v10 as V10,
#                     p.v11 as V11, p.v12 as V12, p.v13 as V13, p.v14 as V14, p.v15 as V15,
#                     p.v16 as V16, p.v17 as V17, p.v18 as V18, p.v19 as V19, p.v20 as V20,
#                     p.v21 as V21, p.v22 as V22, p.v23 as V23, p.v24 as V24, p.v25 as V25,
#                     p.v26 as V26, p.v27 as V27, p.v28 as V28,
#                     p.actual_class as Class
#                 FROM predictions p
#                 WHERE p.actual_class IS NOT NULL
#                 ORDER BY p.feedback_received_at DESC
#             """
            
#             if limit:
#                 query += f" LIMIT {limit}"
            
#             cursor.execute(query)
#             results = cursor.fetchall()
            
#             # Convert to list of dicts with proper types
#             training_data = []
#             for result in results:
#                 row_dict = dict(result)
#                 training_data.append(convert_decimals(row_dict))
            
#             return training_data
            
#     except Exception as e:
#         print(f"❌ Error fetching feedback for retraining: {e}")
#         return []


# def get_daily_stats():
#     """Get daily fraud statistics"""
#     try:
#         with db.get_cursor() as cursor:
#             cursor.execute("SELECT * FROM daily_fraud_stats LIMIT 30")
#             results = cursor.fetchall()
#             return [convert_decimals(dict(r)) for r in results]
#     except Exception as e:
#         print(f"❌ Error fetching daily stats: {e}")
#         return []


# def get_model_performance():
#     """Get model performance metrics"""
#     try:
#         with db.get_cursor() as cursor:
#             cursor.execute("SELECT * FROM model_performance")
#             results = cursor.fetchall()
#             return [convert_decimals(dict(r)) for r in results]
#     except Exception as e:
#         print(f"❌ Error fetching model performance: {e}")
#         return []


# # ============================================
# # INITIALIZATION
# # ============================================

# def init_database():
#     """Initialize database connection"""
#     success = db.initialize_pool()
#     if success:
#         print("✅ Database initialized successfully")
#     else:
#         print("⚠️  Database initialization failed - app will run without DB")
#     return success


# def close_database():
#     """Close database connections"""
#     db.close_all_connections()


# # ============================================
# # TESTING
# # ============================================

# if __name__ == "__main__":
#     print("🧪 Testing database connection...")
    
#     # Initialize
#     if init_database():
#         print("✅ Connection successful")
        
#         # Test query
#         try:
#             with db.get_cursor() as cursor:
#                 cursor.execute("SELECT version FROM model_versions WHERE is_active = TRUE")
#                 result = cursor.fetchone()
#                 if result:
#                     print(f"✅ Active model version: {result['version']}")
#                 else:
#                     print("⚠️  No active model found")
            
#             # Test decimal conversion
#             print("\n🧪 Testing decimal conversion...")
#             predictions = get_recent_predictions(5)
#             if predictions:
#                 print(f"✅ Retrieved {len(predictions)} predictions")
#                 print(f"   First prediction fraud_probability type: {type(predictions[0]['fraud_probability'])}")
#                 print(f"   Value: {predictions[0]['fraud_probability']}")
            
#             # Test feedback count
#             print("\n🧪 Testing feedback count...")
#             count = get_feedback_count()
#             print(f"✅ Total feedback: {count}")
            
#         except Exception as e:
#             print(f"❌ Test query failed: {e}")
        
#         # Close
#         close_database()
#     else:
#         print("❌ Connection failed")



### final fixed one given after production -------------########


# database/db.py - FIXED VERSION (Properly saves V1-V28)
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from decimal import Decimal
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.connection_pool = None
        self.initialize_pool()
    
    def initialize_pool(self):
        """Initialize connection pool"""
        try:
            self.connection_pool = pool.SimpleConnectionPool(
                1, 20,
                host=os.getenv('DB_HOST', 'localhost'),
                port=os.getenv('DB_PORT', 5432),
                database=os.getenv('DB_NAME', 'fraud_detection'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', 'postgres123')
            )
            print("✅ Database connection pool created")
        except Exception as e:
            print(f"❌ Error creating connection pool: {e}")
            self.connection_pool = None
    
    def ensure_pool(self):
        """Ensure connection pool exists"""
        if self.connection_pool is None or self.connection_pool.closed:
            self.initialize_pool()
    
    @contextmanager
    def get_connection(self):
        """Get connection from pool"""
        self.ensure_pool()
        conn = None
        try:
            conn = self.connection_pool.getconn()
            yield conn
        finally:
            if conn:
                self.connection_pool.putconn(conn)
    
    @contextmanager
    def get_cursor(self):
        """Get cursor with RealDictCursor"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            try:
                yield cursor
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                cursor.close()
    
    def close_all(self):
        """Close all connections"""
        if self.connection_pool:
            self.connection_pool.closeall()
            print("✅ All database connections closed")

db = Database()

def convert_decimals(data):
    """Convert Decimal to float for JSON serialization"""
    if isinstance(data, dict):
        return {k: convert_decimals(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_decimals(item) for item in data]
    elif isinstance(data, Decimal):
        return float(data)
    return data

def init_database():
    """Initialize database and create default model version"""
    try:
        with db.get_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM model_versions")
            count = cursor.fetchone()['count']
            
            if count == 0:
                cursor.execute("""
                    INSERT INTO model_versions (version, model_path, threshold, is_active)
                    VALUES ('final_v1.0', 'models/fraud_model_final.json', 0.4, true)
                """)
                print("✅ Database initialized successfully")
            else:
                print("✅ Database already initialized")
        return True
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False

def save_prediction(prediction_data):
    """
    Save prediction to database - FIXED to properly save V1-V28
    
    Args:
        prediction_data: dict with keys:
            - transaction_time: int
            - amount: float
            - V1 to V28: float (ALL V features)
            - prediction: int (0 or 1)
            - fraud_probability: float
            - risk_level: str
            - top_features: dict/list
            - ai_explanation: str
            - model_version_id: int
            - threshold_used: float
    """
    try:
        with db.get_cursor() as cursor:
            # Get active model version
            cursor.execute("SELECT id FROM model_versions WHERE is_active = true LIMIT 1")
            model_version = cursor.fetchone()
            model_version_id = model_version['id'] if model_version else 1
            
            # ✅ FIX: Extract ALL V features with defaults
            v_features = {}
            for i in range(1, 29):
                # Use V{i} (capital V) from input, default to 0 if missing
                v_key = f'V{i}'
                v_features[f'v{i}'] = prediction_data.get(v_key, 0.0)
            
            # Prepare insert query with ALL V columns
            query = '''
                INSERT INTO predictions (
                    transaction_time, amount,
                    v1, v2, v3, v4, v5, v6, v7, v8, v9, v10,
                    v11, v12, v13, v14, v15, v16, v17, v18, v19, v20,
                    v21, v22, v23, v24, v25, v26, v27, v28,
                    prediction, fraud_probability, risk_level,
                    top_features, ai_explanation,
                    model_version_id, threshold_used
                ) VALUES (
                    %(transaction_time)s, %(amount)s,
                    %(v1)s, %(v2)s, %(v3)s, %(v4)s, %(v5)s, %(v6)s, %(v7)s, %(v8)s, %(v9)s, %(v10)s,
                    %(v11)s, %(v12)s, %(v13)s, %(v14)s, %(v15)s, %(v16)s, %(v17)s, %(v18)s, %(v19)s, %(v20)s,
                    %(v21)s, %(v22)s, %(v23)s, %(v24)s, %(v25)s, %(v26)s, %(v27)s, %(v28)s,
                    %(prediction)s, %(fraud_probability)s, %(risk_level)s,
                    %(top_features)s, %(ai_explanation)s,
                    %(model_version_id)s, %(threshold_used)s
                ) RETURNING id
            '''
            
            # Merge V features into data
            insert_data = {
                'transaction_time': prediction_data.get('transaction_time', 0),
                'amount': prediction_data.get('amount', 0.0),
                **v_features,  # ✅ All V1-V28 included
                'prediction': prediction_data.get('prediction', 0),
                'fraud_probability': prediction_data.get('fraud_probability', 0.0),
                'risk_level': prediction_data.get('risk_level', 'UNKNOWN'),
                'top_features': str(prediction_data.get('top_features', {})),
                'ai_explanation': prediction_data.get('ai_explanation', ''),
                'model_version_id': prediction_data.get('model_version_id', model_version_id),
                'threshold_used': prediction_data.get('threshold_used', 0.5)
            }
            
            cursor.execute(query, insert_data)
            prediction_id = cursor.fetchone()['id']
            
            print(f"✅ Prediction saved to database: ID {prediction_id}")
            return prediction_id
            
    except Exception as e:
        print(f"❌ Error saving prediction: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_prediction_by_id(prediction_id):
    """Get prediction by ID"""
    try:
        with db.get_cursor() as cursor:
            query = '''
                SELECT 
                    p.*,
                    mv.version as model_version,
                    mv.threshold as model_threshold
                FROM predictions p
                LEFT JOIN model_versions mv ON p.model_version_id = mv.id
                WHERE p.id = %s
            '''
            cursor.execute(query, (prediction_id,))
            result = cursor.fetchone()
            return convert_decimals(dict(result)) if result else None
    except Exception as e:
        print(f'❌ Error fetching prediction: {e}')
        return None

def get_recent_predictions(limit=50):
    """Get recent predictions"""
    try:
        with db.get_cursor() as cursor:
            query = '''
                SELECT 
                    id, amount, prediction, fraud_probability,
                    risk_level, predicted_at
                FROM predictions
                ORDER BY predicted_at DESC
                LIMIT %s
            '''
            cursor.execute(query, (limit,))
            results = cursor.fetchall()
            return [convert_decimals(dict(r)) for r in results]
    except Exception as e:
        print(f'❌ Error fetching predictions: {e}')
        return []

def update_prediction_feedback(prediction_id, actual_class, feedback_note=''):
    """Update prediction with actual class (feedback)"""
    try:
        with db.get_cursor() as cursor:
            # Update predictions table
            cursor.execute('''
                UPDATE predictions 
                SET actual_class = %s, feedback_received_at = NOW()
                WHERE id = %s
            ''', (actual_class, prediction_id))
            
            # Get prediction details for feedback table
            cursor.execute('''
                SELECT prediction, fraud_probability 
                FROM predictions 
                WHERE id = %s
            ''', (prediction_id,))
            pred_data = cursor.fetchone()
            
            if pred_data:
                # Determine feedback type
                predicted = pred_data['prediction']
                
                if predicted == actual_class:
                    feedback_type = 'correct'
                elif predicted == 1 and actual_class == 0:
                    feedback_type = 'false_positive'
                else:
                    feedback_type = 'false_negative'
                
                # Insert into feedback table
                cursor.execute('''
                    INSERT INTO feedback (
                        prediction_id, feedback_type, feedback_note
                    ) VALUES (%s, %s, %s)
                ''', (prediction_id, feedback_type, feedback_note))
            
            return True
    except Exception as e:
        print(f'❌ Error updating feedback: {e}')
        return False

def get_feedback_count():
    """Get total feedback count"""
    try:
        with db.get_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM predictions WHERE actual_class IS NOT NULL")
            result = cursor.fetchone()
            return result['count'] if result else 0
    except Exception as e:
        print(f'❌ Error getting feedback count: {e}')
        return 0

def close_database():
    """Close database connections"""
    db.close_all()

# Export functions
__all__ = [
    'init_database',
    'close_database',
    'save_prediction',
    'get_prediction_by_id',
    'get_recent_predictions',
    'update_prediction_feedback',
    'get_feedback_count',
    'db'
]