# Railway Deployment Checklist & Troubleshooting

## Current Error Analysis

**Error**: `Failed to load resource: the server responded with a status of 500 ()`
**URL**: `https://frauddetectionsystem-production.up.railway.app/api/check-fraud`

This indicates the backend is deployed but encountering runtime errors.

---

## Step-by-Step Fix


# Required Variables
DATABASE_URL=<automatically set by Railway PostgreSQL>
GROQ_API_KEY=<your-groq-api-key>
PORT=5000

# Optional but Recommended
FRAUD_DETECTION_API_KEY=9M8WmlHhO7t8g1V-KlfDEa7OfmwUbyMd6TvkApXgoKk
FLASK_ENV=production
PYTHONUNBUFFERED=1
```

### 2. Check Railway Logs

In Railway Dashboard:
1. Click on your service
2. Go to "Deployments" tab
3. Click "View logs" on the active deployment
4. Look for error messages

**Common errors to look for:**
- `ModuleNotFoundError` - Missing dependencies
- `Database connection failed` - Database not connected
- `FileNotFoundError` - Missing model files
- `ImportError` - Missing packages

### 3. Fix CORS Configuration

The backend needs to allow requests from your frontend URL.

**Update `app_integrated.py`:**

Find the CORS configuration (around line 25) and update it:

```python
from flask_cors import CORS

# Allow your Vercel/Netlify frontend URL
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:3000",
            "https://frauddetectionsystem-production.up.railway.app",
            "https://*.vercel.app",
            "https://*.netlify.app"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "X-API-Key"]
    }
})
```

### 4. Ensure All Model Files Are Deployed

Railway needs these files in the `models/` directory:
- `fraud_model_banking.json`
- `fraud_model_final.json`
- `features_banking.json`
- `features.json` or `feature_names.json`
- `model_config_banking.json`
- `model_config.json`
- `scaler_banking.pkl`

**Check if they're in your Git repository:**
```bash
git ls-files models/
```

If missing, add them:
```bash
git add models/*.json models/*.pkl
git commit -m "Add model files"
git push
```

### 5. Add Database Schema to Railway

If you haven't run the database schema yet:

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Run schema
railway run psql $DATABASE_URL < database/schema_dual.sql
```

### 6. Create Procfile for Railway

Create a `Procfile` in the root directory:

```bash
web: python app_integrated.py
```

### 7. Create railway.json (Optional)

Create `railway.json` in root:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python app_integrated.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

---

## Quick Debug Commands

### Test Railway Backend Directly

```bash
# Test health endpoint
curl https://frauddetectionsystem-production.up.railway.app/

# Test with verbose output
curl -v https://frauddetectionsystem-production.up.railway.app/api/check-fraud \
  -H "Content-Type: application/json" \
  -H "X-API-Key: 9M8WmlHhO7t8g1V-KlfDEa7OfmwUbyMd6TvkApXgoKk" \
  -d '{
    "mode": "banking",
    "Transaction_Amount": 100,
    "Account_Balance": 5000,
    "Transaction_Type": "POS",
    "Timestamp": "2024-01-17 10:00:00",
    "Daily_Transaction_Count": 1,
    "Avg_Transaction_Amount_7d": 100,
    "Failed_Transaction_Count_7d": 0,
    "Card_Age": 100,
    "Transaction_Distance": 10,
    "IP_Address_Flag": 0
  }'
```

### Check Railway Logs

```bash
railway logs
```

---

## Common Issues & Solutions

### Issue 1: "ModuleNotFoundError"

**Solution**: Update `requirements.txt` and redeploy
```bash
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update requirements"
git push
```

### Issue 2: "Database connection failed"

**Solution**: 
1. Ensure PostgreSQL service is added in Railway
2. Check `DATABASE_URL` is set automatically
3. Verify schema is loaded

### Issue 3: "Model files not found"

**Solution**:
1. Ensure model files are committed to Git
2. Check `.gitignore` doesn't exclude `*.pkl` or `*.json` files
3. If files are large, use Git LFS:
```bash
git lfs install
git lfs track "*.pkl"
git add .gitattributes
git commit -m "Track model files with LFS"
git push
```

### Issue 4: "CORS policy error"

**Solution**: Update CORS configuration in `app_integrated.py` (see Step 3 above)

### Issue 5: "Port already in use"

**Solution**: Railway automatically assigns a port. Ensure your app uses:
```python
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
```

---

## Verification Steps

After making changes:

1. ✅ Push changes to GitHub
2. ✅ Wait for Railway to redeploy (check Deployments tab)
3. ✅ Check logs for errors
4. ✅ Test health endpoint: `curl https://frauddetectionsystem-production.up.railway.app/`
5. ✅ Test fraud detection endpoint with curl (see above)
6. ✅ Test from frontend

---

## Frontend Configuration

Ensure your frontend is properly configured:

### Local Testing with Railway Backend

```bash
# In fraud-detection-ui/.env
REACT_APP_API_URL=https://frauddetectionsystem-production.up.railway.app
REACT_APP_API_KEY=9M8WmlHhO7t8g1V-KlfDEa7OfmwUbyMd6TvkApXgoKk
```

### Deploy Frontend to Vercel

```bash
cd fraud-detection-ui

# Set environment variables
vercel env add REACT_APP_API_URL
# Enter: https://frauddetectionsystem-production.up.railway.app

vercel env add REACT_APP_API_KEY
# Enter: 9M8WmlHhO7t8g1V-KlfDEa7OfmwUbyMd6TvkApXgoKk

# Deploy
vercel --prod
```

---

## Next Steps

1. **Check Railway logs** for specific error messages
2. **Verify environment variables** are set
3. **Test backend directly** with curl
4. **Update CORS** if needed
5. **Redeploy** after fixes

Once backend is working, the frontend will connect successfully!
