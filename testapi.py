
# import requests
# import json

# URL = "http://127.0.0.1:5000"

# print("\n🧪 Simple API Test\n")

# # Step 1: Health check
# print("1. Testing health endpoint...")
# try:
#     r = requests.get(f"{URL}/")
#     print(f"   Status: {r.status_code}")
#     if r.status_code == 200:
#         print(f"   ✅ API is online")
#         print(f"   Response: {r.json()}")
#     else:
#         print(f"   ❌ Health check failed")
#         exit(1)
# except Exception as e:
#     print(f"   ❌ Error: {e}")
#     print("\n   Make sure Flask is running:")
#     print("   python app_debug.py")
#     exit(1)

# # Step 2: Prediction
# print("\n2. Testing prediction...")

# payload = {
#     "Time": 21217,
#     "V1": -3.12, "V2": 4.58, "V3": -1.77, "V4": 6.91, "V5": -0.84,
#     "V6": 2.66, "V7": -5.49, "V8": 3.72, "V9": -2.28, "V10": 7.14,
#     "V11": -6.03, "V12": 0.95, "V13": 4.11, "V14": -7.88, "V15": 1.39,
#     "V16": 2.77, "V17": -4.52, "V18": 3.41, "V19": -0.63, "V20": 6.44,
#     "V21": -8.27, "V22": 4.86, "V23": -2.02, "V24": 1.51, "V25": -5.92,
#     "V26": 2.18, "V27": -1.38, "V28": 3.66,
#     "Amount": 1000
# }

# print(f"   Payload: Amount=${payload['Amount']}, {len(payload)} fields")
# print(f"   Sending POST request...")

# try:
#     r = requests.post(
#         f"{URL}/predict",
#         json=payload,
#         headers={"Content-Type": "application/json"},
#         timeout=30
#     )
    
#     print(f"   Status: {r.status_code}")
    
#     if r.status_code == 200:
#         result = r.json()
#         print(f"   ✅ SUCCESS!")
#         print(f"\n   Results:")
#         print(f"   - Prediction: {result.get('message')}")
#         print(f"   - Fraud Probability: {result.get('fraud_probability')}")
#         print(f"   - Risk Level: {result.get('risk_level', 'N/A')}")
#     else:
#         print(f"   ❌ FAILED with status {r.status_code}")
#         print(f"\n   Response:")
#         print(r.text)
        
#         # Try to get JSON error
#         try:
#             err = r.json()
#             print(f"\n   Error: {err.get('error')}")
#             print(f"   Type: {err.get('error_type')}")
#         except:
#             pass

# except requests.exceptions.Timeout:
#     print(f"   ❌ Request timed out (30 seconds)")
# except Exception as e:
#     print(f"   ❌ Error: {e}")

# print("\n✅ Test complete\n")


import psycopg2
import os

print("="*70)
print("🗄️  FRAUD DETECTION DATABASE SETUP")
print("="*70)

# Database credentials
DB_PASSWORD = input("\nEnter PostgreSQL password: ")

try:
    print("\n🔌 Connecting to fraud_detection database...")
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="fraud_detection",
        user="postgres",
        password=DB_PASSWORD
    )
    
    cursor = conn.cursor()
    print("✅ Connected!")
    
    # Check if tables already exist
    cursor.execute("""
        SELECT COUNT(*) FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = 'predictions'
    """)
    
    table_exists = cursor.fetchone()[0] > 0
    
    if table_exists:
        print("\n⚠️  Tables already exist!")
        response = input("Do you want to DROP and recreate all tables? (yes/no): ")
        
        if response.lower() != 'yes':
            print("❌ Setup cancelled. Existing tables kept.")
            cursor.close()
            conn.close()
            exit()
    
    # Read and execute schema
    print("\n📋 Loading schema from file...")
    schema_path = "database/schema_dual.sql"
    
    if not os.path.exists(schema_path):
        print(f"❌ Schema file not found: {schema_path}")
        print("\nPlease make sure 'schema_duale.sql' is in the 'database' folder")
        cursor.close()
        conn.close()
        exit()
    
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    
    print("📊 Executing schema...")
    cursor.execute(schema_sql)
    conn.commit()
    print("✅ Schema loaded successfully!")
    
    # Verify tables
    print("\n🔍 Verifying tables...")
    cursor.execute("""
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public' 
        ORDER BY tablename
    """)
    
    tables = cursor.fetchall()
    print(f"\n✅ Created {len(tables)} tables:")
    for table in tables:
        print(f"   • {table[0]}")
    
    # Verify views
    cursor.execute("""
        SELECT viewname 
        FROM pg_views 
        WHERE schemaname = 'public' 
        ORDER BY viewname
    """)
    
    views = cursor.fetchall()
    print(f"\n✅ Created {len(views)} views:")
    for view in views:
        print(f"   • {view[0]}")
    
    # Check model versions
    cursor.execute("SELECT id, version, model_type, threshold, is_active FROM model_versions ORDER BY id")
    models = cursor.fetchall()
    
    print(f"\n✅ Loaded {len(models)} model versions:")
    for model in models:
        status = "ACTIVE" if model[4] else "inactive"
        print(f"   • {model[2]}: {model[1]} (threshold: {model[3]}, {status})")
    
    cursor.close()
    conn.close()
    
    # Save credentials to .env
    print("\n💾 Saving configuration...")
    
    env_content = f"""# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=fraud_detection
DB_USER=postgres
DB_PASSWORD={DB_PASSWORD}

# GenAI Configuration
GROQ_API_KEY=your_groq_api_key_here
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("✅ Configuration saved to .env")
    
    print("\n" + "="*70)
    print("✅ DATABASE SETUP COMPLETE!")
    print("="*70)
    
    print("\n📋 Next Steps:")
    print("1. Update .env with your GROQ_API_KEY (for GenAI)")
    print("2. Copy database files:")
    print("   - Copy db_dual.py to database\\db.py")
    print("3. Test connection: python database\\db.py")
    print("4. Update app1.py to use database")
    print("5. Start your app: python app1.py")
    
except psycopg2.Error as e:
    print(f"\n❌ Database Error: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure PostgreSQL service is running")
    print("2. Check your password is correct")
    print("3. Make sure database 'fraud_detection' exists")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

input("\nPress Enter to exit...")