# test_with_api_key.ps1 - Test WITH API Authentication

$baseUrl = "http://localhost:5000"
$apiKey = "9M8WmlHhO7t8g1V-KlfDEa7OfmwUbyMd6TvkApXgoKk"  # Your generated key

Write-Host ""
Write-Host "="*80 -ForegroundColor Cyan
Write-Host "TESTING WITH API AUTHENTICATION" -ForegroundColor Cyan
Write-Host "="*80 -ForegroundColor Cyan
Write-Host ""

# Test 1: WITHOUT API Key (should fail if auth enabled)
Write-Host "[TEST 1] Request WITHOUT API Key" -ForegroundColor Yellow
Write-Host "-"*60

$body = @{
    mode = "banking"
    Transaction_Amount = 100
    Account_Balance = 5000
    Transaction_Type = "POS"
    Timestamp = "2023-12-27 12:00:00"
    Daily_Transaction_Count = 3
    Avg_Transaction_Amount_7d = 80
    Failed_Transaction_Count_7d = 0
    Card_Age = 200
    Transaction_Distance = 300
    IP_Address_Flag = 0
} | ConvertTo-Json

try {
    $result = Invoke-RestMethod -Uri "$baseUrl/api/check-fraud" `
        -Method POST `
        -Body $body `
        -ContentType "application/json" `
        -ErrorAction Stop
    
    Write-Host "  Result: Request succeeded WITHOUT key" -ForegroundColor Yellow
    Write-Host "  This means API auth is DISABLED" -ForegroundColor Yellow
    Write-Host "  (This is OK for development)" -ForegroundColor Gray
} catch {
    if ($_.Exception.Response.StatusCode -eq 401 -or $_.Exception.Response.StatusCode -eq 403) {
        Write-Host "  Result: 401/403 Unauthorized" -ForegroundColor Green
        Write-Host "  API auth is WORKING!" -ForegroundColor Green
    } else {
        Write-Host "  Error: $_" -ForegroundColor Red
    }
}

# Test 2: WITH API Key (should always work)
Write-Host "`n[TEST 2] Request WITH API Key" -ForegroundColor Yellow
Write-Host "-"*60

$headers = @{
    "X-API-Key" = $apiKey
}

try {
    $result = Invoke-RestMethod -Uri "$baseUrl/api/check-fraud" `
        -Method POST `
        -Headers $headers `
        -Body $body `
        -ContentType "application/json"
    
    Write-Host "  [OK] Request succeeded WITH key" -ForegroundColor Green
    Write-Host "  Prediction ID: $($result.prediction_id)" -ForegroundColor Cyan
    Write-Host "  Is Fraud: $($result.is_fraud)" -ForegroundColor Cyan
    Write-Host "  Confidence: $($result.fraud_probability * 100)%" -ForegroundColor Cyan
} catch {
    Write-Host "  [FAIL] Error: $_" -ForegroundColor Red
}

Write-Host "`n"
Write-Host "="*80 -ForegroundColor Cyan
Write-Host ""

# Instructions
Write-Host "TO ENABLE API AUTHENTICATION:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Make sure your .env file has:" -ForegroundColor White
Write-Host "   FRAUD_DETECTION_API_KEY=$apiKey" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Restart Flask:" -ForegroundColor White
Write-Host "   Ctrl+C to stop" -ForegroundColor Gray
Write-Host "   python app.py" -ForegroundColor Gray
Write-Host ""
Write-Host "3. You'll see: 'API auth: ENABLED'" -ForegroundColor White
Write-Host ""
Write-Host "4. Then Test 1 will FAIL (401) and Test 2 will PASS" -ForegroundColor White
Write-Host ""
Write-Host "="*80 -ForegroundColor Cyan