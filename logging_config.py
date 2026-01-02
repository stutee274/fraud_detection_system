# logging_config.py - Phase 6: Comprehensive Logging System
"""
Centralized logging configuration for fraud detection system
Logs: API requests, predictions, feedback, retraining, errors
"""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
import json

# Create logs directory
LOGS_DIR = "logs"
os.makedirs(LOGS_DIR, exist_ok=True)

# Log files
API_LOG = os.path.join(LOGS_DIR, "api.log")
PREDICTIONS_LOG = os.path.join(LOGS_DIR, "predictions.log")
RETRAINING_LOG = os.path.join(LOGS_DIR, "retraining.log")
SECURITY_LOG = os.path.join(LOGS_DIR, "security.log")
ERROR_LOG = os.path.join(LOGS_DIR, "errors.log")

# Custom JSON formatter
class JSONFormatter(logging.Formatter):
    """Format logs as JSON for easy parsing"""
    
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add extra fields if present
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'ip_address'):
            log_data['ip_address'] = record.ip_address
        if hasattr(record, 'prediction_id'):
            log_data['prediction_id'] = record.prediction_id
        if hasattr(record, 'model_type'):
            log_data['model_type'] = record.model_type
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)

# Configure rotating file handlers (10MB max, 5 backups)
def create_rotating_handler(filename, max_bytes=10*1024*1024, backup_count=5):
    """Create a rotating file handler"""
    handler = RotatingFileHandler(
        filename,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    handler.setFormatter(JSONFormatter())
    return handler

# API Logger
api_logger = logging.getLogger('api')
api_logger.setLevel(logging.INFO)
api_logger.addHandler(create_rotating_handler(API_LOG))

# Predictions Logger
predictions_logger = logging.getLogger('predictions')
predictions_logger.setLevel(logging.INFO)
predictions_logger.addHandler(create_rotating_handler(PREDICTIONS_LOG))

# Retraining Logger
retraining_logger = logging.getLogger('retraining')
retraining_logger.setLevel(logging.INFO)
retraining_logger.addHandler(create_rotating_handler(RETRAINING_LOG))

# Security Logger
security_logger = logging.getLogger('security')
security_logger.setLevel(logging.WARNING)
security_logger.addHandler(create_rotating_handler(SECURITY_LOG))

# Error Logger
error_logger = logging.getLogger('errors')
error_logger.setLevel(logging.ERROR)
error_logger.addHandler(create_rotating_handler(ERROR_LOG))

# Helper functions for common logging patterns
def log_api_request(endpoint, method, ip_address, user_id=None, params=None):
    """Log API request"""
    api_logger.info(
        f"API Request: {method} {endpoint}",
        extra={
            'ip_address': ip_address,
            'user_id': user_id,
            'params': params
        }
    )

def log_prediction(prediction_id, model_type, prediction, confidence, ip_address):
    """Log fraud prediction"""
    predictions_logger.info(
        f"Prediction made: ID {prediction_id}",
        extra={
            'prediction_id': prediction_id,
            'model_type': model_type,
            'prediction': prediction,
            'confidence': confidence,
            'ip_address': ip_address
        }
    )

def log_feedback(prediction_id, actual_class, feedback_type):
    """Log feedback submission"""
    predictions_logger.info(
        f"Feedback received: ID {prediction_id}",
        extra={
            'prediction_id': prediction_id,
            'actual_class': actual_class,
            'feedback_type': feedback_type
        }
    )

def log_retraining(model_type, samples_used, old_f1, new_f1, activated):
    """Log model retraining"""
    retraining_logger.info(
        f"Retraining completed: {model_type}",
        extra={
            'model_type': model_type,
            'samples_used': samples_used,
            'old_f1': old_f1,
            'new_f1': new_f1,
            'improvement': new_f1 - old_f1,
            'activated': activated
        }
    )

def log_security_event(event_type, severity, message, ip_address, user_id=None):
    """Log security event"""
    security_logger.warning(
        f"Security Event: {event_type} - {message}",
        extra={
            'event_type': event_type,
            'severity': severity,
            'ip_address': ip_address,
            'user_id': user_id
        }
    )

def log_error(error_type, message, exc_info=None):
    """Log error"""
    error_logger.error(
        f"Error: {error_type} - {message}",
        exc_info=exc_info
    )

# Console handler for development (optional)
def add_console_handler():
    """Add console output for development"""
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    
    for logger in [api_logger, predictions_logger, retraining_logger, security_logger, error_logger]:
        logger.addHandler(console)

# Initialize logging
print(f"✅ Logging configured:")
print(f"   API logs:         {API_LOG}")
print(f"   Predictions logs: {PREDICTIONS_LOG}")
print(f"   Retraining logs:  {RETRAINING_LOG}")
print(f"   Security logs:    {SECURITY_LOG}")
print(f"   Error logs:       {ERROR_LOG}")