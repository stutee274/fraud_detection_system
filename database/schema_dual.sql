-- schema_dual_complete.sql - Complete Dual Mode Database Schema
-- Supports BOTH Banking (raw features) and Credit Card (V1-V28) models
-- Includes timestamp tracking for banking transactions

-- ============================================
-- DROP EXISTING TABLES
-- ============================================
DROP TABLE IF EXISTS feedback CASCADE;
DROP TABLE IF EXISTS predictions CASCADE;
DROP TABLE IF EXISTS model_versions CASCADE;

-- ============================================
-- TABLE 1: Model Versions
-- ============================================
CREATE TABLE model_versions (
    id SERIAL PRIMARY KEY,
    version VARCHAR(50) NOT NULL UNIQUE,
    model_type VARCHAR(20) NOT NULL CHECK (model_type IN ('banking', 'credit_card')),
    model_path VARCHAR(255) NOT NULL,
    threshold DECIMAL(5, 4) NOT NULL,
    performance_metrics JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT FALSE,
    description TEXT
);

CREATE INDEX idx_model_active ON model_versions(is_active);
CREATE INDEX idx_model_type ON model_versions(model_type);

COMMENT ON TABLE model_versions IS 'Stores different model versions for both banking and credit card fraud detection';
COMMENT ON COLUMN model_versions.model_type IS 'Either banking or credit_card';

-- ============================================
-- TABLE 2: Predictions (Dual Mode Support)
-- ============================================
CREATE TABLE predictions (
    -- ========================================
    -- PRIMARY KEY & METADATA
    -- ========================================
    id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(100) UNIQUE,  -- Optional external ID
    model_type VARCHAR(20) NOT NULL CHECK (model_type IN ('banking', 'credit_card')),
    
    -- ========================================
    -- COMMON FIELDS (Both Models)
    -- ========================================
    amount DECIMAL(12, 2) NOT NULL,
    transaction_time BIGINT,  -- Original Time field from dataset
    
    -- Transaction datetime (for banking mode)
    transaction_datetime TIMESTAMP,  -- Actual date/time of transaction
    transaction_date DATE,  -- Just the date
    transaction_hour INTEGER,  -- Hour of day (0-23)
    
    -- ========================================
    -- BANKING MODE SPECIFIC FEATURES
    -- ========================================
    -- Raw banking data
    account_balance DECIMAL(12, 2),
    transaction_type VARCHAR(50),  -- ATM, POS, Online, Transfer
    daily_transaction_count INTEGER,
    avg_transaction_amount_7d DECIMAL(12, 2),
    failed_transaction_count_7d INTEGER,
    card_age INTEGER,  -- Days since card issued
    transaction_distance DECIMAL(10, 2),  -- Distance from home (km)
    ip_address_flag INTEGER,  -- 0=safe, 1=suspicious
    
    -- Derived banking features (for analytics)
    spend_ratio DECIMAL(8, 6),
    amount_vs_avg DECIMAL(8, 6),
    late_night BOOLEAN,
    is_weekend BOOLEAN,
    new_card BOOLEAN,
    far_transaction BOOLEAN,
    high_daily_count BOOLEAN,
    
    -- ========================================
    -- CREDIT CARD MODE FEATURES (V1-V28 PCA)
    -- ========================================
    v1 DECIMAL(10, 6), v2 DECIMAL(10, 6), v3 DECIMAL(10, 6), v4 DECIMAL(10, 6),
    v5 DECIMAL(10, 6), v6 DECIMAL(10, 6), v7 DECIMAL(10, 6), v8 DECIMAL(10, 6),
    v9 DECIMAL(10, 6), v10 DECIMAL(10, 6), v11 DECIMAL(10, 6), v12 DECIMAL(10, 6),
    v13 DECIMAL(10, 6), v14 DECIMAL(10, 6), v15 DECIMAL(10, 6), v16 DECIMAL(10, 6),
    v17 DECIMAL(10, 6), v18 DECIMAL(10, 6), v19 DECIMAL(10, 6), v20 DECIMAL(10, 6),
    v21 DECIMAL(10, 6), v22 DECIMAL(10, 6), v23 DECIMAL(10, 6), v24 DECIMAL(10, 6),
    v25 DECIMAL(10, 6), v26 DECIMAL(10, 6), v27 DECIMAL(10, 6), v28 DECIMAL(10, 6),
    
    -- ========================================
    -- PREDICTION RESULTS (Common to Both)
    -- ========================================
    prediction INTEGER NOT NULL CHECK (prediction IN (0, 1)),  -- 0=normal, 1=fraud
    fraud_probability DECIMAL(8, 6) NOT NULL,
    risk_level VARCHAR(20),  -- MINIMAL, LOW, MEDIUM, HIGH, CRITICAL
    threshold_used DECIMAL(5, 4) NOT NULL,
    
    -- Explanations
    top_features JSONB,  -- SHAP top contributing features
    ai_explanation TEXT,  -- GenAI natural language explanation
    ai_provider VARCHAR(50),  -- groq, gemini, fallback
    
    -- ========================================
    -- MODEL & AUDIT INFORMATION
    -- ========================================
    model_version_id INTEGER REFERENCES model_versions(id),
    predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    api_endpoint VARCHAR(100),
    request_ip VARCHAR(45),
    request_user_agent TEXT,
    
    -- ========================================
    -- FEEDBACK (For Model Improvement)
    -- ========================================
    actual_class INTEGER CHECK (actual_class IN (0, 1, NULL)),  -- NULL = no feedback yet
    feedback_received_at TIMESTAMP,
    feedback_source VARCHAR(50),  -- api, manual, investigation
    
    -- ========================================
    -- ADDITIONAL METADATA
    -- ========================================
    notes TEXT,  -- Any additional notes
    is_flagged_for_review BOOLEAN DEFAULT FALSE,
    reviewed_at TIMESTAMP,
    reviewed_by VARCHAR(100)
);

-- Indexes for performance
CREATE INDEX idx_predictions_time ON predictions(predicted_at DESC);
CREATE INDEX idx_predictions_date ON predictions(transaction_date DESC);
CREATE INDEX idx_predictions_fraud ON predictions(prediction);
CREATE INDEX idx_predictions_model_type ON predictions(model_type);
CREATE INDEX idx_predictions_amount ON predictions(amount);
CREATE INDEX idx_predictions_risk ON predictions(risk_level);
CREATE INDEX idx_predictions_feedback ON predictions(actual_class) WHERE actual_class IS NOT NULL;
CREATE INDEX idx_predictions_flagged ON predictions(is_flagged_for_review) WHERE is_flagged_for_review = TRUE;

COMMENT ON TABLE predictions IS 'Stores predictions from both banking and credit card fraud models';
COMMENT ON COLUMN predictions.model_type IS 'Identifies which model was used: banking or credit_card';
COMMENT ON COLUMN predictions.transaction_datetime IS 'Actual date/time of transaction (banking mode only)';
COMMENT ON COLUMN predictions.transaction_time IS 'Seconds since first transaction (original dataset field)';

-- ============================================
-- TABLE 3: Feedback (User Corrections)
-- ============================================
CREATE TABLE feedback (
    id SERIAL PRIMARY KEY,
    prediction_id INTEGER REFERENCES predictions(id) ON DELETE CASCADE,
    
    -- Feedback details
    actual_class INTEGER NOT NULL CHECK (actual_class IN (0, 1)),
    feedback_type VARCHAR(50),  -- false_positive, false_negative, true_positive, true_negative
    feedback_note TEXT,
    confidence_level INTEGER CHECK (confidence_level BETWEEN 1 AND 5),  -- 1=low, 5=high
    
    -- Source
    feedback_source VARCHAR(50),  -- api, analyst, customer, investigation
    user_id VARCHAR(100),
    user_role VARCHAR(50),  -- analyst, admin, system, customer
    
    -- Investigation details (if applicable)
    investigation_id VARCHAR(100),
    investigation_notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_feedback_prediction ON feedback(prediction_id);
CREATE INDEX idx_feedback_time ON feedback(created_at DESC);
CREATE INDEX idx_feedback_type ON feedback(feedback_type);
CREATE INDEX idx_feedback_source ON feedback(feedback_source);

COMMENT ON TABLE feedback IS 'Stores user feedback on predictions for model improvement';
COMMENT ON COLUMN feedback.confidence_level IS 'User confidence in their feedback (1-5)';

-- ============================================
-- TABLE 4: Model Performance Tracking
-- ============================================
CREATE TABLE model_performance_log (
    id SERIAL PRIMARY KEY,
    model_version_id INTEGER REFERENCES model_versions(id),
    evaluation_date DATE DEFAULT CURRENT_DATE,
    
    -- Performance metrics
    total_predictions INTEGER,
    total_with_feedback INTEGER,
    accuracy DECIMAL(6, 4),
    precision DECIMAL(6, 4),
    recall DECIMAL(6, 4),
    f1_score DECIMAL(6, 4),
    
    -- Confusion matrix
    true_positives INTEGER,
    true_negatives INTEGER,
    false_positives INTEGER,
    false_negatives INTEGER,
    
    -- Additional metrics
    avg_fraud_probability DECIMAL(6, 4),
    fraud_detection_rate DECIMAL(6, 4),
    false_alarm_rate DECIMAL(6, 4),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_perf_log_model ON model_performance_log(model_version_id);
CREATE INDEX idx_perf_log_date ON model_performance_log(evaluation_date DESC);

-- ============================================
-- VIEWS FOR ANALYTICS
-- ============================================

-- View 1: Daily Stats by Model Type
CREATE VIEW daily_stats_by_model AS
SELECT 
    model_type,
    DATE(predicted_at) as date,
    COUNT(*) as total_transactions,
    SUM(CASE WHEN prediction = 1 THEN 1 ELSE 0 END) as fraud_detected,
    SUM(CASE WHEN prediction = 0 THEN 1 ELSE 0 END) as normal_transactions,
    ROUND(AVG(fraud_probability), 4) as avg_fraud_probability,
    SUM(CASE WHEN prediction = 1 THEN amount ELSE 0 END) as fraud_amount,
    ROUND(AVG(amount), 2) as avg_transaction_amount,
    
    -- With feedback
    COUNT(CASE WHEN actual_class IS NOT NULL THEN 1 END) as with_feedback,
    COUNT(CASE WHEN prediction = actual_class THEN 1 END) as correct_predictions
FROM predictions
GROUP BY model_type, DATE(predicted_at)
ORDER BY date DESC, model_type;

-- View 2: Model Performance Comparison
CREATE VIEW model_performance_comparison AS
SELECT 
    mv.model_type,
    mv.version,
    mv.threshold,
    COUNT(p.id) as total_predictions,
    
    -- Predictions
    SUM(CASE WHEN p.prediction = 1 THEN 1 ELSE 0 END) as fraud_flagged,
    SUM(CASE WHEN p.prediction = 0 THEN 1 ELSE 0 END) as normal_flagged,
    
    -- With feedback
    COUNT(CASE WHEN p.actual_class IS NOT NULL THEN 1 END) as with_feedback,
    
    -- Accuracy metrics (where feedback exists)
    COUNT(CASE WHEN p.prediction = p.actual_class THEN 1 END) as correct,
    COUNT(CASE WHEN p.prediction = 1 AND p.actual_class = 1 THEN 1 END) as true_positives,
    COUNT(CASE WHEN p.prediction = 0 AND p.actual_class = 0 THEN 1 END) as true_negatives,
    COUNT(CASE WHEN p.prediction = 1 AND p.actual_class = 0 THEN 1 END) as false_positives,
    COUNT(CASE WHEN p.prediction = 0 AND p.actual_class = 1 THEN 1 END) as false_negatives,
    
    -- Rates
    ROUND(AVG(p.fraud_probability), 4) as avg_fraud_probability
FROM model_versions mv
LEFT JOIN predictions p ON p.model_version_id = mv.id
WHERE mv.is_active = TRUE
GROUP BY mv.id, mv.model_type, mv.version, mv.threshold;

-- View 3: Recent High Risk Transactions
CREATE VIEW high_risk_transactions AS
SELECT 
    id,
    model_type,
    transaction_id,
    amount,
    fraud_probability,
    risk_level,
    CASE 
        WHEN model_type = 'banking' THEN transaction_datetime
        ELSE predicted_at
    END as transaction_time,
    ai_explanation,
    predicted_at,
    is_flagged_for_review,
    actual_class
FROM predictions
WHERE prediction = 1 
  AND predicted_at > NOW() - INTERVAL '7 days'
ORDER BY fraud_probability DESC, predicted_at DESC
LIMIT 100;

-- View 4: Feedback Summary
CREATE VIEW feedback_summary AS
SELECT 
    p.model_type,
    DATE(f.created_at) as feedback_date,
    COUNT(*) as total_feedback,
    SUM(CASE WHEN f.feedback_type = 'false_positive' THEN 1 ELSE 0 END) as false_positives,
    SUM(CASE WHEN f.feedback_type = 'false_negative' THEN 1 ELSE 0 END) as false_negatives,
    SUM(CASE WHEN f.feedback_type = 'true_positive' THEN 1 ELSE 0 END) as true_positives,
    SUM(CASE WHEN f.feedback_type = 'true_negative' THEN 1 ELSE 0 END) as true_negatives,
    ROUND(AVG(f.confidence_level), 2) as avg_confidence
FROM feedback f
JOIN predictions p ON f.prediction_id = p.id
GROUP BY p.model_type, DATE(f.created_at)
ORDER BY feedback_date DESC;

-- View 5: Hourly Fraud Patterns (Banking Mode)
CREATE VIEW hourly_fraud_patterns AS
SELECT 
    transaction_hour,
    COUNT(*) as total_transactions,
    SUM(CASE WHEN prediction = 1 THEN 1 ELSE 0 END) as fraud_detected,
    ROUND(100.0 * SUM(CASE WHEN prediction = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) as fraud_rate,
    ROUND(AVG(amount), 2) as avg_amount,
    ROUND(AVG(fraud_probability), 4) as avg_fraud_prob
FROM predictions
WHERE model_type = 'banking' AND transaction_hour IS NOT NULL
GROUP BY transaction_hour
ORDER BY transaction_hour;

-- ============================================
-- FUNCTIONS FOR DATA QUERIES
-- ============================================

-- Function 1: Get predictions needing feedback
CREATE OR REPLACE FUNCTION get_predictions_needing_feedback(
    p_limit INTEGER DEFAULT 20,
    p_model_type VARCHAR DEFAULT NULL
)
RETURNS TABLE(
    prediction_id INTEGER,
    model_type VARCHAR,
    amount DECIMAL,
    fraud_probability DECIMAL,
    predicted_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.id,
        p.model_type,
        p.amount,
        p.fraud_probability,
        p.predicted_at
    FROM predictions p
    WHERE p.actual_class IS NULL
      AND p.prediction = 1  -- Focus on fraud predictions
      AND (p_model_type IS NULL OR p.model_type = p_model_type)
    ORDER BY p.fraud_probability DESC, p.predicted_at DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Function 2: Calculate model accuracy
CREATE OR REPLACE FUNCTION calculate_model_accuracy(
    p_model_type VARCHAR
)
RETURNS TABLE(
    total_with_feedback BIGINT,
    accuracy DECIMAL,
    precision DECIMAL,
    recall DECIMAL,
    f1_score DECIMAL
) AS $$
DECLARE
    tp INTEGER;
    tn INTEGER;
    fp INTEGER;
    fn INTEGER;
    prec DECIMAL;
    rec DECIMAL;
BEGIN
    -- Get confusion matrix
    SELECT 
        COUNT(CASE WHEN prediction = 1 AND actual_class = 1 THEN 1 END),
        COUNT(CASE WHEN prediction = 0 AND actual_class = 0 THEN 1 END),
        COUNT(CASE WHEN prediction = 1 AND actual_class = 0 THEN 1 END),
        COUNT(CASE WHEN prediction = 0 AND actual_class = 1 THEN 1 END)
    INTO tp, tn, fp, fn
    FROM predictions
    WHERE model_type = p_model_type
      AND actual_class IS NOT NULL;
    
    -- Calculate metrics
    prec := CASE WHEN (tp + fp) > 0 THEN ROUND(tp::DECIMAL / (tp + fp), 4) ELSE 0 END;
    rec := CASE WHEN (tp + fn) > 0 THEN ROUND(tp::DECIMAL / (tp + fn), 4) ELSE 0 END;
    
    RETURN QUERY
    SELECT 
        (tp + tn + fp + fn)::BIGINT,
        CASE WHEN (tp + tn + fp + fn) > 0 THEN ROUND((tp + tn)::DECIMAL / (tp + tn + fp + fn), 4) ELSE 0 END,
        prec,
        rec,
        CASE WHEN (prec + rec) > 0 THEN ROUND(2 * prec * rec / (prec + rec), 4) ELSE 0 END;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- INITIAL DATA
-- ============================================

-- Insert Banking Model Version
INSERT INTO model_versions (
    version, model_type, model_path, threshold, is_active, description
) VALUES (
    'banking_v1.0',
    'banking',
    'models/fraud_model_banking.pkl',
    0.3,
    TRUE,
    'Random Forest model for banking transactions with raw features'
);

-- Insert Credit Card Model Version
INSERT INTO model_versions (
    version, model_type, model_path, threshold, is_active, description
) VALUES (
    'credit_card_v1.0',
    'credit_card',
    'models/fraud_model_final.json',
    0.4,
    TRUE,
    'XGBoost model for credit card transactions with V1-V28 PCA features'
);

-- ============================================
-- TRIGGERS FOR AUTO-UPDATE
-- ============================================

-- Trigger: Auto-update feedback_received_at
CREATE OR REPLACE FUNCTION update_prediction_feedback()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.actual_class IS NOT NULL AND OLD.actual_class IS NULL THEN
        NEW.feedback_received_at = CURRENT_TIMESTAMP;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_feedback
BEFORE UPDATE ON predictions
FOR EACH ROW
EXECUTE FUNCTION update_prediction_feedback();

-- Trigger: Auto-update feedback.updated_at
CREATE OR REPLACE FUNCTION update_feedback_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_feedback_time
BEFORE UPDATE ON feedback
FOR EACH ROW
EXECUTE FUNCTION update_feedback_timestamp();

COMMIT;

-- ============================================
-- VERIFICATION
-- ============================================
SELECT 'Database schema created successfully!' as status;
SELECT '✅ Tables created: model_versions, predictions, feedback, model_performance_log' as info;
SELECT '✅ Views created: daily_stats_by_model, model_performance_comparison, high_risk_transactions, feedback_summary, hourly_fraud_patterns' as info;
SELECT '✅ Functions created: get_predictions_needing_feedback(), calculate_model_accuracy()' as info;

-- Show created model versions
SELECT 
    id, version, model_type, threshold, is_active, description
FROM model_versions
ORDER BY model_type, id;