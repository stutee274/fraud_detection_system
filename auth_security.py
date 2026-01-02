# auth_security.py - Phase 6: Authentication & Security
"""
API Authentication, Rate Limiting, and Security Features
"""

from functools import wraps
from flask import request, jsonify
import os
from datetime import datetime, timedelta
import hashlib
import secrets
from logging_config import log_security_event, security_logger

# Configuration
API_KEYS = {}  # Will be loaded from environment or database
RATE_LIMIT = {
    'max_requests': 100,  # Max requests per window
    'window_minutes': 15   # Time window in minutes
}

# In-memory rate limiting (use Redis in production)
request_history = {}

# ============================================
# API KEY MANAGEMENT
# ============================================
def generate_api_key():
    """Generate a secure API key"""
    return secrets.token_urlsafe(32)

def hash_api_key(api_key):
    """Hash API key for storage"""
    return hashlib.sha256(api_key.encode()).hexdigest()

def load_api_keys():
    """Load API keys from environment"""
    global API_KEYS
    
    # Load from environment (format: KEY_NAME=api_key_value)
    master_key = os.getenv('FRAUD_DETECTION_API_KEY')
    if master_key:
        API_KEYS['master'] = hash_api_key(master_key)
        print("✅ Master API key loaded")
    else:
        print("⚠️  No API key configured (AUTH DISABLED)")

# ============================================
# AUTHENTICATION DECORATOR
# ============================================
def require_api_key(f):
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if authentication is enabled
        if not API_KEYS:
            # Auth disabled - allow request
            return f(*args, **kwargs)
        
        # Get API key from header
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            log_security_event(
                'AUTH_FAILURE',
                'HIGH',
                'Missing API key',
                request.remote_addr
            )
            return jsonify({
                'status': 'error',
                'message': 'API key required'
            }), 401
        
        # Validate API key
        key_hash = hash_api_key(api_key)
        if key_hash not in API_KEYS.values():
            log_security_event(
                'AUTH_FAILURE',
                'HIGH',
                'Invalid API key',
                request.remote_addr
            )
            return jsonify({
                'status': 'error',
                'message': 'Invalid API key'
            }), 403
        
        # Authentication successful
        return f(*args, **kwargs)
    
    return decorated_function

# ============================================
# RATE LIMITING
# ============================================
def check_rate_limit(ip_address):
    """Check if IP has exceeded rate limit"""
    now = datetime.now()
    window_start = now - timedelta(minutes=RATE_LIMIT['window_minutes'])
    
    # Clean old entries
    if ip_address in request_history:
        request_history[ip_address] = [
            timestamp for timestamp in request_history[ip_address]
            if timestamp > window_start
        ]
    else:
        request_history[ip_address] = []
    
    # Check limit
    if len(request_history[ip_address]) >= RATE_LIMIT['max_requests']:
        return False
    
    # Add current request
    request_history[ip_address].append(now)
    return True

def rate_limit(f):
    """Decorator for rate limiting"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        ip_address = request.remote_addr
        
        if not check_rate_limit(ip_address):
            log_security_event(
                'RATE_LIMIT_EXCEEDED',
                'MEDIUM',
                f'Rate limit exceeded: {len(request_history[ip_address])} requests',
                ip_address
            )
            return jsonify({
                'status': 'error',
                'message': 'Rate limit exceeded. Try again later.',
                'retry_after': RATE_LIMIT['window_minutes'] * 60
            }), 429
        
        return f(*args, **kwargs)
    
    return decorated_function

# ============================================
# INPUT VALIDATION
# ============================================
def validate_banking_input(data):
    """Validate banking transaction input"""
    required_fields = [
        'Transaction_Amount', 'Account_Balance', 'Transaction_Type',
        'Timestamp', 'Daily_Transaction_Count', 'Avg_Transaction_Amount_7d',
        'Failed_Transaction_Count_7d', 'Card_Age', 'Transaction_Distance',
        'IP_Address_Flag'
    ]
    
    # Check required fields
    missing = [f for f in required_fields if f not in data]
    if missing:
        return False, f"Missing fields: {', '.join(missing)}"
    
    # Validate data types and ranges
    try:
        amount = float(data['Transaction_Amount'])
        if amount < 0 or amount > 1000000:
            return False, "Transaction amount out of valid range (0-1M)"
        
        balance = float(data['Account_Balance'])
        if balance < 0:
            return False, "Account balance cannot be negative"
        
        return True, None
    except (ValueError, TypeError) as e:
        return False, f"Invalid data type: {str(e)}"

def validate_credit_card_input(data):
    """Validate credit card transaction input"""
    required_fields = ['Time', 'Amount'] + [f'V{i}' for i in range(1, 29)]
    
    # Check required fields
    missing = [f for f in required_fields if f not in data]
    if missing:
        return False, f"Missing fields: {', '.join(missing)}"
    
    try:
        amount = float(data['Amount'])
        if amount < 0 or amount > 100000:
            return False, "Amount out of valid range (0-100K)"
        
        return True, None
    except (ValueError, TypeError) as e:
        return False, f"Invalid data type: {str(e)}"

# ============================================
# SECURITY HEADERS
# ============================================
def add_security_headers(response):
    """Add security headers to response"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response

# ============================================
# INITIALIZE
# ============================================
def initialize_security(app):
    """Initialize security features"""
    
    # Load API keys
    load_api_keys()
    
    # Add security headers to all responses
    @app.after_request
    def apply_security_headers(response):
        return add_security_headers(response)
    
    print("✅ Security initialized")
    print(f"   Rate limit: {RATE_LIMIT['max_requests']} req/{RATE_LIMIT['window_minutes']}min")
    print(f"   API auth: {'ENABLED' if API_KEYS else 'DISABLED'}")