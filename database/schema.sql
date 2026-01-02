# database/schema.sql - PostgreSQL Database Schema for Fraud Detection

-- ============================================
-- PHASE 3: DATABASE SCHEMA
-- ============================================

-- Drop existing tables (if any)
DROP TABLE IF EXISTS feedback CASCADE;
DROP TABLE IF EXISTS predictions CASCADE;
DROP TABLE IF EXISTS model_versions CASCADE;

-- ============================================
-- TABLE 1: Model Versions
-- ============================================
CREATE TABLE model_versions (
    id SERIAL PRIMARY KEY,
    version VARCHAR(50) NOT NULL UNIQUE,
    model_path VARCHAR(255) NOT NULL,
    threshold DECIMAL(5, 4) NOT NULL,
    performance_metrics JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT FALSE
);

-- Create index on active models
CREATE INDEX idx_model_active ON model_versions(is_active);

-- ============================================
-- TABLE 2: Predictions (MAIN TABLE)
-- ============================================
CREATE TABLE predictions (
    -- Primary Key
    id SERIAL PRIMARY KEY,
    
    -- Transaction Data
    transaction_id VARCHAR(100) UNIQUE,  -- Optional: external transaction ID
    transaction_time BIGINT NOT NULL,     -- Original Time field
    amount DECIMAL(12, 2) NOT NULL,
    
    -- All V features (PCA components from original dataset)
    v1 DECIMAL(10, 6), v2 DECIMAL(10, 6), v3 DECIMAL(10, 6), v4 DECIMAL(10, 6),
    v5 DECIMAL(10, 6), v6 DECIMAL(10, 6), v7 DECIMAL(10, 6), v8 DECIMAL(10, 6),
    v9 DECIMAL(10, 6), v10 DECIMAL(10, 6), v11 DECIMAL(10, 6), v12 DECIMAL(10, 6),
    v13 DECIMAL(10, 6), v14 DECIMAL(10, 6), v15 DECIMAL(10, 6), v16 DECIMAL(10, 6),
    v17 DECIMAL(10, 6), v18 DECIMAL(10, 6), v19 DECIMAL(10, 6), v20 DECIMAL(10, 6),
    v21 DECIMAL(10, 6), v22 DECIMAL(10, 6), v23 DECIMAL(10, 6), v24 DECIMAL(10, 6),
    v25 DECIMAL(10, 6), v26 DECIMAL(10, 6), v27 DECIMAL(10, 6), v28 DECIMAL(10, 6),
    
    -- Prediction Results
    prediction INTEGER NOT NULL CHECK (prediction IN (0, 1)),  -- 0=normal, 1=fraud
    fraud_probability DECIMAL(8, 6) NOT NULL,
    risk_level VARCHAR(20),
    threshold_used DECIMAL(5, 4) NOT NULL,
    
    -- Explanations (stored as JSON)
    top_features JSONB,           -- SHAP top features
    ai_explanation TEXT,           -- Gemini/Groq explanation
    ai_provider VARCHAR(50),       -- "Gemini" or "Groq"
    
    -- Model Information
    model_version_id INTEGER REFERENCES model_versions(id),
    
    -- Audit Trail
    predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    api_endpoint VARCHAR(100),
    request_ip VARCHAR(45),
    
    -- Actual Label (for feedback)
    actual_class INTEGER CHECK (actual_class IN (0, 1, NULL)),
    feedback_received_at TIMESTAMP
);

-- Create indexes for common queries
CREATE INDEX idx_predictions_time ON predictions(predicted_at DESC);
CREATE INDEX idx_predictions_fraud ON predictions(prediction);
CREATE INDEX idx_predictions_amount ON predictions(amount);
CREATE INDEX idx_predictions_model ON predictions(model_version_id);
CREATE INDEX idx_predictions_transaction_time ON predictions(transaction_time);

-- ============================================
-- TABLE 3: Feedback (User corrections)
-- ============================================
CREATE TABLE feedback (
    id SERIAL PRIMARY KEY,
    prediction_id INTEGER REFERENCES predictions(id) ON DELETE CASCADE,
    
    -- Feedback details
    actual_class INTEGER NOT NULL CHECK (actual_class IN (0, 1)),
    feedback_type VARCHAR(50),  -- "false_positive", "false_negative", "correct"
    feedback_note TEXT,
    
    -- Who provided feedback
    user_id VARCHAR(100),
    user_role VARCHAR(50),  -- "analyst", "admin", "system"
    
    -- When
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_feedback_prediction ON feedback(prediction_id);
CREATE INDEX idx_feedback_time ON feedback(created_at DESC);

-- ============================================
-- VIEWS FOR ANALYTICS
-- ============================================

-- View 1: Daily Fraud Stats
CREATE VIEW daily_fraud_stats AS
SELECT 
    DATE(predicted_at) as date,
    COUNT(*) as total_transactions,
    SUM(CASE WHEN prediction = 1 THEN 1 ELSE 0 END) as fraud_detected,
    SUM(CASE WHEN prediction = 1 THEN amount ELSE 0 END) as fraud_amount,
    AVG(fraud_probability) as avg_fraud_prob,
    AVG(amount) as avg_amount
FROM predictions
GROUP BY DATE(predicted_at)
ORDER BY date DESC;

-- View 2: Model Performance
CREATE VIEW model_performance AS
SELECT 
    mv.version,
    mv.threshold,
    COUNT(p.id) as predictions_count,
    SUM(CASE WHEN p.prediction = 1 THEN 1 ELSE 0 END) as fraud_flagged,
    SUM(CASE WHEN p.actual_class = 1 THEN 1 ELSE 0 END) as actual_fraud,
    SUM(CASE WHEN p.prediction = p.actual_class THEN 1 ELSE 0 END) as correct_predictions,
    AVG(p.fraud_probability) as avg_probability
FROM model_versions mv
LEFT JOIN predictions p ON p.model_version_id = mv.id
WHERE p.actual_class IS NOT NULL
GROUP BY mv.id, mv.version, mv.threshold;

-- View 3: Recent High-Risk Transactions
CREATE VIEW high_risk_recent AS
SELECT 
    id,
    transaction_id,
    amount,
    fraud_probability,
    risk_level,
    ai_explanation,
    predicted_at
FROM predictions
WHERE prediction = 1 
  AND predicted_at > NOW() - INTERVAL '24 hours'
ORDER BY fraud_probability DESC, predicted_at DESC;

-- ============================================
-- INITIAL DATA
-- ============================================

-- Insert current model version
INSERT INTO model_versions (version, model_path, threshold, performance_metrics, is_active)
VALUES (
    'final_v1.0',
    'models/fraud_model_final.json',
    0.40,
    '{"roc_auc": 0.9787, "f1_score": 0.6078, "recall": 0.878, "precision": 0.465}'::jsonb,
    TRUE
);

-- ============================================
-- USEFUL QUERIES (for reference)
-- ============================================

-- Get fraud rate by hour
-- SELECT EXTRACT(HOUR FROM predicted_at) as hour, 
--        COUNT(*) as total,
--        SUM(CASE WHEN prediction = 1 THEN 1 ELSE 0 END) as frauds
-- FROM predictions
-- GROUP BY EXTRACT(HOUR FROM predicted_at)
-- ORDER BY hour;

-- Get accuracy where feedback exists
-- SELECT 
--     COUNT(*) as total,
--     SUM(CASE WHEN prediction = actual_class THEN 1 ELSE 0 END) as correct,
--     ROUND(100.0 * SUM(CASE WHEN prediction = actual_class THEN 1 ELSE 0 END) / COUNT(*), 2) as accuracy
-- FROM predictions
-- WHERE actual_class IS NOT NULL;

-- Get top features that flag fraud
-- SELECT 
--     jsonb_array_elements(top_features)->>'feature' as feature,
--     COUNT(*) as times_in_top,
--     AVG((jsonb_array_elements(top_features)->>'contribution')::numeric) as avg_contribution
-- FROM predictions
-- WHERE prediction = 1
-- GROUP BY jsonb_array_elements(top_features)->>'feature'
-- ORDER BY times_in_top DESC
-- LIMIT 10;

COMMIT;