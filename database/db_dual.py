# database/db_dual.py - RAILWAY PRODUCTION VERSION
"""
Database module for Railway deployment with DATABASE_URL support
Supports both Railway (DATABASE_URL) and local development (DB_HOST, etc.)
"""

import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from decimal import Decimal
from datetime import datetime
import json
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================
# HELPER FUNCTIONS
# ============================================
def convert_decimals(obj):
    """Convert Decimal to float for JSON serialization"""
    if isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimals(item) for item in obj]
    elif isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    return obj

# ============================================
# DATABASE CLASS (RAILWAY COMPATIBLE)
# ============================================
class Database:
    """Database connection manager with Railway support"""
    
    def __init__(self):
        self.connection_pool = None
        
        # Check if DATABASE_URL exists (Railway/Production)
        database_url = os.getenv('DATABASE_URL')
        
        if database_url:
            # PRODUCTION MODE (Railway)
            print("🚀 Using DATABASE_URL (Production Mode)")
            self.config = {'dsn': database_url}
            self.use_dsn = True
        else:
            # DEVELOPMENT MODE (Local)
            print("🔧 Using individual DB vars (Development Mode)")
            self.config = {
                'host': os.getenv('DB_HOST', 'localhost'),
                'port': int(os.getenv('DB_PORT', 5432)),
                'database': os.getenv('DB_NAME', 'fraud_detection'),
                'user': os.getenv('DB_USER', 'postgres'),
                'password': os.getenv('DB_PASSWORD', 'postgres')
            }
            self.use_dsn = False
    
    def initialize_pool(self, minconn=1, maxconn=20):
        """Initialize connection pool"""
        try:
            if self.connection_pool is not None:
                try:
                    self.connection_pool.closeall()
                except:
                    pass
            
            if self.use_dsn:
                # Railway: Use DATABASE_URL
                self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                    minconn, maxconn, **self.config
                )
            else:
                # Local: Use individual parameters
                self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                    minconn, maxconn, **self.config
                )
            
            print("✅ Database connection pool created")
            return True
        except Exception as e:
            print(f"❌ Error creating connection pool: {e}")
            print(f"   Config: {self.config if not self.use_dsn else 'DATABASE_URL'}")
            return False
    
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

# Global database instance
db = Database()

# ============================================
# SAVE PREDICTION (DUAL MODE)
# ============================================
def save_prediction_to_db(prediction_data):
    """
    Save prediction to database (supports both banking and credit card)
    """
    try:
        with db.get_cursor() as cursor:
            # Get model type
            model_type = prediction_data.get('mode', 'banking')
            
            # Get active model version
            cursor.execute("""
                SELECT id FROM model_versions 
                WHERE model_type = %s AND is_active = true 
                LIMIT 1
            """, (model_type,))
            
            model_version = cursor.fetchone()
            model_version_id = model_version['id'] if model_version else 1
            
            # Common fields
            common_data = {
                'model_type': model_type,
                'prediction': prediction_data.get('prediction', 0),
                'fraud_probability': float(prediction_data.get('fraud_probability', 0)),
                'risk_level': prediction_data.get('risk_level', 'UNKNOWN'),
                'threshold_used': float(prediction_data.get('threshold_used', 0.5)),
                'top_features': json.dumps(prediction_data.get('top_features', [])),
                'ai_explanation': prediction_data.get('ai_explanation', ''),
                'ai_provider': prediction_data.get('ai_provider', 'fallback'),
                'model_version_id': model_version_id,
                'api_endpoint': prediction_data.get('api_endpoint', '/api/check-fraud'),
                'request_ip': prediction_data.get('request_ip', 'unknown')
            }
            
            if model_type == 'banking':
                # BANKING MODE
                amount = float(prediction_data.get('Transaction_Amount', 0))
                
                # Parse timestamp
                timestamp_str = prediction_data.get('Timestamp', '')
                try:
                    dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    transaction_datetime = dt
                    transaction_date = dt.date()
                    transaction_hour = dt.hour
                except:
                    transaction_datetime = datetime.now()
                    transaction_date = transaction_datetime.date()
                    transaction_hour = transaction_datetime.hour
                
                # Banking specific fields
                banking_data = {
                    'amount': amount,
                    'transaction_datetime': transaction_datetime,
                    'transaction_date': transaction_date,
                    'transaction_hour': transaction_hour,
                    'account_balance': float(prediction_data.get('Account_Balance', 0)),
                    'transaction_type': prediction_data.get('Transaction_Type', 'POS'),
                    'daily_transaction_count': int(prediction_data.get('Daily_Transaction_Count', 0)),
                    'avg_transaction_amount_7d': float(prediction_data.get('Avg_Transaction_Amount_7d', 0)),
                    'failed_transaction_count_7d': int(prediction_data.get('Failed_Transaction_Count_7d', 0)),
                    'card_age': int(prediction_data.get('Card_Age', 0)),
                    'transaction_distance': float(prediction_data.get('Transaction_Distance', 0)),
                    'ip_address_flag': int(prediction_data.get('IP_Address_Flag', 0))
                }
                
                # Merge with common data
                insert_data = {**common_data, **banking_data}
                
                # Insert query for banking
                query = """
                    INSERT INTO predictions (
                        model_type, amount, transaction_datetime, transaction_date, transaction_hour,
                        account_balance, transaction_type, daily_transaction_count,
                        avg_transaction_amount_7d, failed_transaction_count_7d,
                        card_age, transaction_distance, ip_address_flag,
                        prediction, fraud_probability, risk_level, threshold_used,
                        top_features, ai_explanation, ai_provider,
                        model_version_id, api_endpoint, request_ip
                    ) VALUES (
                        %(model_type)s, %(amount)s, %(transaction_datetime)s, %(transaction_date)s, %(transaction_hour)s,
                        %(account_balance)s, %(transaction_type)s, %(daily_transaction_count)s,
                        %(avg_transaction_amount_7d)s, %(failed_transaction_count_7d)s,
                        %(card_age)s, %(transaction_distance)s, %(ip_address_flag)s,
                        %(prediction)s, %(fraud_probability)s, %(risk_level)s, %(threshold_used)s,
                        %(top_features)s, %(ai_explanation)s, %(ai_provider)s,
                        %(model_version_id)s, %(api_endpoint)s, %(request_ip)s
                    ) RETURNING id
                """
                
            else:
                # CREDIT CARD MODE
                amount = float(prediction_data.get('Amount', 0))
                transaction_time = int(prediction_data.get('Time', 0))
                
                # Extract V1-V28
                v_features = {}
                for i in range(1, 29):
                    v_key = f'V{i}'
                    v_features[f'v{i}'] = float(prediction_data.get(v_key, 0))
                
                # Credit card specific fields
                cc_data = {
                    'amount': amount,
                    'transaction_time': transaction_time,
                    **v_features
                }
                
                # Merge with common data
                insert_data = {**common_data, **cc_data}
                
                # Insert query for credit card
                query = """
                    INSERT INTO predictions (
                        model_type, amount, transaction_time,
                        v1, v2, v3, v4, v5, v6, v7, v8, v9, v10,
                        v11, v12, v13, v14, v15, v16, v17, v18, v19, v20,
                        v21, v22, v23, v24, v25, v26, v27, v28,
                        prediction, fraud_probability, risk_level, threshold_used,
                        top_features, ai_explanation, ai_provider,
                        model_version_id, api_endpoint, request_ip
                    ) VALUES (
                        %(model_type)s, %(amount)s, %(transaction_time)s,
                        %(v1)s, %(v2)s, %(v3)s, %(v4)s, %(v5)s, %(v6)s, %(v7)s, %(v8)s, %(v9)s, %(v10)s,
                        %(v11)s, %(v12)s, %(v13)s, %(v14)s, %(v15)s, %(v16)s, %(v17)s, %(v18)s, %(v19)s, %(v20)s,
                        %(v21)s, %(v22)s, %(v23)s, %(v24)s, %(v25)s, %(v26)s, %(v27)s, %(v28)s,
                        %(prediction)s, %(fraud_probability)s, %(risk_level)s, %(threshold_used)s,
                        %(top_features)s, %(ai_explanation)s, %(ai_provider)s,
                        %(model_version_id)s, %(api_endpoint)s, %(request_ip)s
                    ) RETURNING id
                """
            
            # Execute insert
            cursor.execute(query, insert_data)
            prediction_id = cursor.fetchone()['id']
            
            print(f"✅ Prediction saved: ID {prediction_id} ({model_type} mode)")
            return prediction_id
            
    except Exception as e:
        print(f"❌ Error saving prediction: {e}")
        import traceback
        traceback.print_exc()
        return None

# ============================================
# GET PREDICTIONS
# ============================================
def get_prediction_by_id(prediction_id):
    """Get prediction by ID"""
    try:
        with db.get_cursor() as cursor:
            query = """
                SELECT p.*, mv.version as model_version, mv.threshold as model_threshold
                FROM predictions p
                LEFT JOIN model_versions mv ON p.model_version_id = mv.id
                WHERE p.id = %s
            """
            cursor.execute(query, (prediction_id,))
            result = cursor.fetchone()
            return convert_decimals(dict(result)) if result else None
    except Exception as e:
        print(f"❌ Error fetching prediction: {e}")
        return None

def get_recent_predictions(limit=50, model_type=None):
    """Get recent predictions"""
    try:
        with db.get_cursor() as cursor:
            if model_type:
                query = """
                    SELECT id, model_type, amount, prediction, fraud_probability,
                           risk_level, predicted_at
                    FROM predictions
                    WHERE model_type = %s
                    ORDER BY predicted_at DESC
                    LIMIT %s
                """
                cursor.execute(query, (model_type, limit))
            else:
                query = """
                    SELECT id, model_type, amount, prediction, fraud_probability,
                           risk_level, predicted_at
                    FROM predictions
                    ORDER BY predicted_at DESC
                    LIMIT %s
                """
                cursor.execute(query, (limit,))
            
            results = cursor.fetchall()
            return [convert_decimals(dict(r)) for r in results]
    except Exception as e:
        print(f"❌ Error fetching predictions: {e}")
        return []

# ============================================
# FEEDBACK MANAGEMENT
# ============================================
def update_prediction_feedback(prediction_id, actual_class, feedback_note='', confidence_level=3):
    """Update prediction with feedback"""
    try:
        with db.get_cursor() as cursor:
            cursor.execute("""
                UPDATE predictions 
                SET actual_class = %s, feedback_received_at = NOW()
                WHERE id = %s
            """, (actual_class, prediction_id))
            
            cursor.execute("""
                SELECT prediction, fraud_probability 
                FROM predictions 
                WHERE id = %s
            """, (prediction_id,))
            pred_data = cursor.fetchone()
            
            if pred_data:
                predicted = pred_data['prediction']
                
                if predicted == actual_class:
                    feedback_type = 'true_positive' if actual_class == 1 else 'true_negative'
                else:
                    feedback_type = 'false_positive' if predicted == 1 else 'false_negative'
                
                cursor.execute("""
                    INSERT INTO feedback (
                        prediction_id, actual_class, feedback_type, 
                        feedback_note, confidence_level, feedback_source
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                """, (prediction_id, actual_class, feedback_type, feedback_note, confidence_level, 'api'))
                
                print(f"✅ Feedback recorded: ID {prediction_id}, Type: {feedback_type}")
            
            return True
    except Exception as e:
        print(f"❌ Error updating feedback: {e}")
        return False

def get_feedback_count(model_type=None, days=30):
    """Get feedback count"""
    try:
        with db.get_cursor() as cursor:
            if model_type:
                cursor.execute("""
                    SELECT COUNT(*) as count 
                    FROM predictions p
                    WHERE p.actual_class IS NOT NULL
                      AND p.model_type = %s
                      AND p.feedback_received_at > NOW() - INTERVAL '%s days'
                """, (model_type, days))
            else:
                cursor.execute("""
                    SELECT COUNT(*) as count 
                    FROM predictions
                    WHERE actual_class IS NOT NULL
                      AND feedback_received_at > NOW() - INTERVAL '%s days'
                """, (days,))
            
            result = cursor.fetchone()
            return result['count'] if result else 0
    except Exception as e:
        print(f"❌ Error getting feedback count: {e}")
        return 0

def get_feedback_data_for_retraining(model_type, limit=None):
    """Get feedback data for model retraining"""
    try:
        with db.get_cursor() as cursor:
            if model_type == 'banking':
                query = """
                    SELECT 
                        amount as "Transaction_Amount",
                        account_balance as "Account_Balance",
                        daily_transaction_count as "Daily_Transaction_Count",
                        failed_transaction_count_7d as "Failed_Transaction_Count_7d",
                        card_age as "Card_Age",
                        transaction_distance as "Transaction_Distance",
                        actual_class as "Class"
                    FROM predictions
                    WHERE model_type = 'banking'
                      AND actual_class IS NOT NULL
                    ORDER BY feedback_received_at DESC
                """
            else:
                query = """
                    SELECT 
                        transaction_time as "Time",
                        amount as "Amount",
                        v1 as "V1", v2 as "V2", v3 as "V3", v4 as "V4", v5 as "V5",
                        v6 as "V6", v7 as "V7", v8 as "V8", v9 as "V9", v10 as "V10",
                        v11 as "V11", v12 as "V12", v13 as "V13", v14 as "V14", v15 as "V15",
                        v16 as "V16", v17 as "V17", v18 as "V18", v19 as "V19", v20 as "V20",
                        v21 as "V21", v22 as "V22", v23 as "V23", v24 as "V24", v25 as "V25",
                        v26 as "V26", v27 as "V27", v28 as "V28",
                        actual_class as "Class"
                    FROM predictions
                    WHERE model_type = 'credit_card'
                      AND actual_class IS NOT NULL
                    ORDER BY feedback_received_at DESC
                """
            
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            if not results:
                print(f"⚠️  No feedback data for {model_type}")
                return []
            
            data_list = []
            for r in results:
                row_dict = convert_decimals(dict(r))
                if 'Class' in row_dict:
                    data_list.append(row_dict)
            
            print(f"✅ Retrieved {len(data_list)} feedback samples for {model_type}")
            return data_list
            
    except Exception as e:
        print(f"❌ Error fetching retraining data: {e}")
        import traceback
        traceback.print_exc()
        return []

# ============================================
# ANALYTICS
# ============================================
def get_daily_stats(days=7, model_type=None):
    """Get daily statistics"""
    try:
        with db.get_cursor() as cursor:
            if model_type:
                cursor.execute("SELECT * FROM daily_stats_by_model WHERE model_type = %s AND date >= CURRENT_DATE - INTERVAL '%s days' ORDER BY date DESC", (model_type, days))
            else:
                cursor.execute("SELECT * FROM daily_stats_by_model WHERE date >= CURRENT_DATE - INTERVAL '%s days' ORDER BY date DESC", (days,))
            
            results = cursor.fetchall()
            return [convert_decimals(dict(r)) for r in results]
    except Exception as e:
        print(f"❌ Error fetching daily stats: {e}")
        return []

def get_model_performance():
    """Get model performance metrics"""
    try:
        with db.get_cursor() as cursor:
            cursor.execute("SELECT * FROM model_performance_comparison")
            results = cursor.fetchall()
            return [convert_decimals(dict(r)) for r in results]
    except Exception as e:
        print(f"❌ Error fetching model performance: {e}")
        return []

def setup_schema_if_needed():
    """Check if tables exist and create them if they don't"""
    try:
        with db.get_cursor() as cursor:
            # Check if predictions table exists (as a proxy for the whole schema)
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'predictions'
                )
            """)
            exists = cursor.fetchone()['exists']
            
            if not exists:
                print("⚠️  Database tables missing. Initializing schema...")
                
                # Try multiple possible paths for schema file
                schema_paths = [
                    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schema_dual.sql'),
                    os.path.join(os.getcwd(), 'database', 'schema_dual.sql'),
                    'schema_dual.sql'
                ]
                
                schema_path = None
                for p in schema_paths:
                    if os.path.exists(p):
                        schema_path = p
                        break
                
                if schema_path:
                    with open(schema_path, 'r') as f:
                        schema_sql = f.read()
                    
                    # Remove lines starting with COMMIT or SELECT verification for script stability
                    clean_sql = "\n".join([line for line in schema_sql.split('\n') 
                                        if not line.strip().upper().startswith('COMMIT')
                                        and not line.strip().upper().startswith('SELECT')])
                    
                    cursor.execute(clean_sql)
                    print("✅ Database schema initialized successfully")
                else:
                    print(f"❌ Schema file (schema_dual.sql) not found in expected locations.")
            else:
                # print("✅ Database tables found")
                pass
                
    except Exception as e:
        print(f"❌ Error setting up database schema: {e}")

# ============================================
# INITIALIZATION
# ============================================
def init_database():
    """Initialize database connection"""
    success = db.initialize_pool()
    if success:
        print("✅ Database connection pool created")
        # Try to setup schema
        setup_schema_if_needed()
        print("✅ Database initialization complete")
    else:
        print("⚠️  Database initialization failed - continuing without DB")
    return success

def close_database():
    """Close database connections"""
    try:
        if db.connection_pool and not db.connection_pool.closed:
            db.close_all()
    except Exception as e:
        # Ignore if pool already closed
        pass

if __name__ == "__main__":
    print("\n🧪 Testing Database Connection...")
    
    if init_database():
        print("✅ Connection successful\n")
        close_database()
    else:
        print("❌ Connection failed")