# Fraud Detection System - Setup Guide

## 🚀 Quick Start

### Backend (Integrated System)

The integrated backend (`app.py`) includes:
- ✅ Dual Mode: Banking + Credit Card fraud detection
- ✅ Database: PostgreSQL with prediction tracking
- ✅ Feedback: User feedback collection and tracking
- ✅ Analytics: Dashboard statistics
- ✅ Retraining: Auto-retraining when feedback threshold reached
- ✅ GenAI: AI-powered explanations

**Start the backend:**
```bash
# Make sure you're in the project root
cd fraud_detection

# Activate virtual environment
.\venv\Scripts\activate

# Start the integrated server
python app.py
```

The server will start on `http://localhost:5000`

### Frontend (React Application)

**Start the frontend:**
```bash
# Navigate to frontend directory
cd fraud-detection-ui

# Start the development server
npm start
```

The UI will open at `http://localhost:3000`

## 📊 System Architecture

### Backend Components

1. **app.py** - Main integrated application
   - Dual-mode fraud detection (Banking + Credit Card)
   - Database integration
   - Analytics and retraining routes
   
2. **database/db_dual.py** - Database layer
   - PostgreSQL connection management
   - Prediction storage
   - Feedback tracking
   
3. **analytics_routes.py** - Analytics endpoints
   - Dashboard statistics
   - Model performance metrics
   
4. **retraining_routes.py** - Model retraining
   - Auto-retraining triggers
   - Feedback-based model updates
   
5. **auth_security.py** - Security features
   - API key authentication
   - Rate limiting

### Frontend Components

1. **App.js** - Main router component
   - Authentication handling (Clerk or Demo mode)
   - Route management
   
2. **pages/Dashboard.jsx** - Main dashboard
   - Mode selector (Banking/Credit Card)
   - Transaction forms
   - Results display
   - Statistics
   
3. **services/api.js** - API client
   - Fraud detection requests
   - Feedback submission
   - Statistics fetching

## 🔧 Configuration

### Environment Variables

**Backend (.env in project root):**
```env
# Database (PostgreSQL)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=fraud_detection
DB_USER=postgres
DB_PASSWORD=your_password

# Or use DATABASE_URL for Railway/Production
DATABASE_URL=postgresql://user:pass@host:port/dbname

# GenAI (Optional)
GROQ_API_KEY=your_groq_api_key

# Security (Optional)
FRAUD_DETECTION_API_KEY=your_api_key
```

**Frontend (.env in fraud-detection-ui/):**
```env
REACT_APP_API_URL=http://localhost:5000
REACT_APP_API_KEY=9M8WmlHhO7t8g1V-KlfDEa7OfmwUbyMd6TvkApXgoKk
REACT_APP_CLERK_PUBLISHABLE_KEY=your_clerk_key  # Optional
```

## 📡 API Endpoints

### Fraud Detection
- `POST /api/check-fraud` - Check transaction for fraud
  ```json
  {
    "mode": "banking",
    "Transaction_Amount": 5000,
    "Account_Balance": 1000,
    "Timestamp": "2023-10-27 23:30:00",
    "Transaction_Type": "Online",
    "Daily_Transaction_Count": 15,
    "Avg_Transaction_Amount_7d": 500,
    "Failed_Transaction_Count_7d": 3,
    "Card_Age": 10,
    "Transaction_Distance": 5000,
    "IP_Address_Flag": 1
  }
  ```

### Feedback
- `POST /api/predictions/{id}/feedback` - Submit feedback
  ```json
  {
    "actual_class": 1,
    "feedback_note": "Confirmed fraud"
  }
  ```

### Analytics
- `GET /api/stats` - Get basic statistics
- `GET /api/analytics/dashboard` - Get dashboard data
- `GET /api/analytics/daily-stats` - Get daily statistics
- `GET /api/analytics/model-performance` - Get model performance

### Retraining
- `GET /api/retrain/status` - Get retraining status
- `POST /api/retrain/trigger` - Manually trigger retraining

## 🎯 Features

### 1. Dual Mode Detection
- **Banking Mode**: Raw transaction data (amount, balance, type, etc.)
- **Credit Card Mode**: PCA features (V1-V28) + Amount + Time

### 2. Database Integration
- All predictions saved to PostgreSQL
- Feedback tracking for model improvement
- Historical data for analytics

### 3. User Feedback
- Submit actual fraud status for predictions
- Automatic retraining trigger when threshold reached
- Feedback statistics and accuracy tracking

### 4. Analytics Dashboard
- Total predictions and fraud rate
- Model performance metrics
- Daily/hourly trends
- Risk distribution

### 5. Auto-Retraining
- Automatically triggers when feedback count reaches threshold (default: 50)
- Uses feedback data to improve model
- Maintains model versions

### 6. AI Explanations
- SHAP-based feature importance
- GenAI-powered natural language explanations
- Top contributing features

## 🔍 Testing the System

### Test Banking Mode
```bash
curl -X POST http://localhost:5000/api/check-fraud \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "banking",
    "Transaction_Amount": 5000,
    "Account_Balance": 1000,
    "Timestamp": "2023-10-27 23:30:00",
    "Transaction_Type": "Online",
    "Daily_Transaction_Count": 15,
    "Avg_Transaction_Amount_7d": 500,
    "Failed_Transaction_Count_7d": 3,
    "Card_Age": 10,
    "Transaction_Distance": 5000,
    "IP_Address_Flag": 1
  }'
```

### Test Credit Card Mode
```bash
curl -X POST http://localhost:5000/api/check-fraud \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "credit_card",
    "Time": 12345,
    "Amount": 100.50,
    "V1": -1.359807,
    "V2": -0.072781,
    ...
    "V28": 0.014724
  }'
```

## 🐛 Troubleshooting

### Backend won't start
- Check if port 5000 is available
- Verify database connection (if using DB)
- Check environment variables

### Frontend can't connect
- Ensure backend is running on port 5000
- Check REACT_APP_API_URL in .env
- Verify CORS is enabled

### Database errors
- Ensure PostgreSQL is running
- Verify database credentials
- Run schema initialization if needed

### Model not found
- Ensure model files exist in `models/` directory
- Check file names match code expectations
- Verify model was trained correctly

## 📝 Notes

- **Demo Mode**: Frontend works without Clerk authentication if `REACT_APP_CLERK_PUBLISHABLE_KEY` is not set
- **Database Optional**: Backend works without database (predictions won't be saved)
- **GenAI Optional**: System uses fallback explanations if GenAI is not configured
- **Auto-Retraining**: Requires database and feedback data

## 🔐 Security

- API key authentication (optional)
- Rate limiting (100 requests per 15 minutes)
- Input validation
- SQL injection protection
- CORS configuration

## 📚 Additional Resources

- Model training scripts: `train_banking.py`, `train_final.py`
- Database schema: `database/schema_dual.sql`
- Feature engineering: `features/features_eng.py`
- Logging configuration: `logging_config.py`
