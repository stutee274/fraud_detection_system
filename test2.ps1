# trigger_auto_retraining.ps1
# Generate 5 more feedbacks to reach threshold of 20 and trigger auto-retraining

Write-Host "`n======================================================================"
Write-Host "TRIGGERING AUTOMATIC RETRAINING"
Write-Host "======================================================================`n"
Write-Host "Current: 15 feedbacks" -ForegroundColor Yellow
Write-Host "Target: 20 feedbacks" -ForegroundColor Green
Write-Host "Need: 5 more samples" -ForegroundColor Cyan
Write-Host ""

$apiUrl = "http://localhost:5000"

# 5 diverse test cases
$finalCases = @(
    @{
        name = "Sample 16 - Normal Shopping"
        Time = 35000; Amount = 156.50
        V1 = 0.38; V2 = 0.55; V3 = -0.15; V4 = 0.65; V5 = 0.22
        V6 = 0.45; V7 = -0.22; V8 = 0.35; V9 = 0.15; V10 = 0.48
        V11 = 0.32; V12 = 0.15; V13 = -0.15; V14 = 0.42; V15 = 0.22
        V16 = 0.38; V17 = -0.22; V18 = 0.22; V19 = 0.15; V20 = 0.22
        V21 = 0.38; V22 = 0.22; V23 = 0.15; V24 = 0.22; V25 = 0.15
        V26 = 0.22; V27 = 0.15; V28 = 0.15
        actual = 0
    },
    @{
        name = "Sample 17 - Fraud Pattern"
        Time = 68000; Amount = 225.00
        V1 = -0.75; V2 = 0.85; V3 = 0.12; V4 = 0.58; V5 = -0.12
        V6 = 0.32; V7 = 0.12; V8 = 0.05; V9 = -0.18; V10 = 0.95
        V11 = 0.68; V12 = -1.15; V13 = 0.32; V14 = -2.15; V15 = 0.48
        V16 = -0.58; V17 = -1.28; V18 = -0.42; V19 = 0.18; V20 = 0.08
        V21 = 0.25; V22 = 0.38; V23 = -0.08; V24 = -0.28; V25 = 0.25
        V26 = -0.38; V27 = 0.02; V28 = 0.02
        actual = 1
    },
    @{
        name = "Sample 18 - Normal Purchase"
        Time = 41000; Amount = 98.75
        V1 = 0.42; V2 = 0.58; V3 = -0.18; V4 = 0.68; V5 = 0.25
        V6 = 0.48; V7 = -0.25; V8 = 0.38; V9 = 0.18; V10 = 0.52
        V11 = 0.35; V12 = 0.18; V13 = -0.18; V14 = 0.48; V15 = 0.25
        V16 = 0.42; V17 = -0.25; V18 = 0.25; V19 = 0.18; V20 = 0.25
        V21 = 0.42; V22 = 0.25; V23 = 0.18; V24 = 0.25; V25 = 0.18
        V26 = 0.25; V27 = 0.18; V28 = 0.18
        actual = 0
    },
    @{
        name = "Sample 19 - Suspicious Transaction"
        Time = 77000; Amount = 345.00
        V1 = -0.65; V2 = 0.75; V3 = 0.10; V4 = 0.52; V5 = -0.10
        V6 = 0.28; V7 = 0.10; V8 = 0.04; V9 = -0.15; V10 = 0.85
        V11 = 0.62; V12 = -1.05; V13 = 0.28; V14 = -1.95; V15 = 0.42
        V16 = -0.52; V17 = -1.15; V18 = -0.38; V19 = 0.15; V20 = 0.07
        V21 = 0.22; V22 = 0.35; V23 = -0.07; V24 = -0.25; V25 = 0.22
        V26 = -0.35; V27 = 0.02; V28 = 0.02
        actual = 1
    },
    @{
        name = "Sample 20 - Regular Transaction (TRIGGER POINT!)"
        Time = 55000; Amount = 178.50
        V1 = 0.45; V2 = 0.62; V3 = -0.20; V4 = 0.72; V5 = 0.28
        V6 = 0.52; V7 = -0.28; V8 = 0.42; V9 = 0.20; V10 = 0.58
        V11 = 0.38; V12 = 0.20; V13 = -0.20; V14 = 0.52; V15 = 0.28
        V16 = 0.45; V17 = -0.28; V18 = 0.28; V19 = 0.20; V20 = 0.28
        V21 = 0.45; V22 = 0.28; V23 = 0.20; V24 = 0.28; V25 = 0.20
        V26 = 0.28; V27 = 0.20; V28 = 0.20
        actual = 0
    }
)

$currentCount = 15

foreach ($case in $finalCases) {
    $currentCount++
    
    Write-Host "[$currentCount/20] $($case.name)" -ForegroundColor Yellow
    
    try {
        # Make prediction
        $data = $case.Clone()
        $data.Remove('name')
        $data.Remove('actual')
        $body = $data | ConvertTo-Json
        
        $result = Invoke-RestMethod -Uri "$apiUrl/predict_explain" -Method POST -Body $body -ContentType "application/json" -ErrorAction Stop
        
        Write-Host "  Predicted: $(if ($result.prediction -eq 1) { 'FRAUD' } else { 'NORMAL' })" -ForegroundColor $(if ($result.prediction -eq 1) { "Red" } else { "Green" })
        Write-Host "  Probability: $([math]::Round($result.fraud_probability * 100, 1))%" -ForegroundColor White
        
        # Submit feedback
        Start-Sleep -Milliseconds 500
        
        $feedback = @{
            actual_class = $case.actual
            feedback_note = "Retraining trigger test - Sample $currentCount"
        } | ConvertTo-Json
        
        $fbResult = Invoke-RestMethod -Uri "$apiUrl/api/predictions/$($result.prediction_id)/feedback" -Method POST -Body $feedback -ContentType "application/json" -ErrorAction Stop
        
        Write-Host "  Actual: $(if ($case.actual -eq 1) { 'FRAUD' } else { 'NORMAL' })" -ForegroundColor $(if ($case.actual -eq 1) { "Red" } else { "Green" })
        Write-Host "  Feedback submitted!" -ForegroundColor Green
        
        if ($currentCount -eq 20) {
            Write-Host "`n  ****************************************" -ForegroundColor Cyan
            Write-Host "  *** REACHED 20 FEEDBACKS! ***" -ForegroundColor Green
            Write-Host "  *** AUTO-RETRAINING SHOULD TRIGGER! ***" -ForegroundColor Green
            Write-Host "  ****************************************" -ForegroundColor Cyan
            Write-Host ""
        }
        
        Write-Host ""
        Start-Sleep -Seconds 2
        
    } catch {
        Write-Host "  [ERROR] $($_.Exception.Message)" -ForegroundColor Red
        Write-Host ""
    }
}

Write-Host "======================================================================"
Write-Host "SAMPLES GENERATED"
Write-Host "======================================================================`n"

Write-Host "CHECK FLASK TERMINAL NOW!" -ForegroundColor Yellow -BackgroundColor DarkBlue
Write-Host "You should see automatic retraining starting..." -ForegroundColor Yellow
Write-Host ""

# Wait a bit for trigger to happen
Start-Sleep -Seconds 5

# Check retraining status
Write-Host "Checking retraining status..." -ForegroundColor Cyan

try {
    $status = Invoke-RestMethod -Uri "$apiUrl/api/retraining/status" -Method GET
    
    Write-Host "`n=== RETRAINING STATUS ===" -ForegroundColor Cyan
    Write-Host "Is Running: $($status.retraining.is_running)" -ForegroundColor $(if ($status.retraining.is_running) { "Green" } else { "White" })
    Write-Host "Last Run: $($status.retraining.last_run)" -ForegroundColor White
    Write-Host "Last Result: $($status.retraining.last_result)" -ForegroundColor White
    Write-Host "Runs Count: $($status.retraining.runs_count)" -ForegroundColor White
    
    if ($status.retraining.is_running) {
        Write-Host "`n🔄 RETRAINING IS RUNNING IN BACKGROUND!" -ForegroundColor Green
        Write-Host "This will take 2-5 minutes..." -ForegroundColor Yellow
        Write-Host "Watch Flask terminal for progress" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Monitor with: Invoke-RestMethod -Uri 'http://localhost:5000/api/retraining/status'" -ForegroundColor Gray
    } elseif ($status.retraining.last_result -eq 'success') {
        Write-Host "`n✅ RETRAINING COMPLETED SUCCESSFULLY!" -ForegroundColor Green
        Write-Host "Message: $($status.retraining.last_message)" -ForegroundColor White
    } else {
        Write-Host "`n⚠️  Retraining may not have triggered automatically" -ForegroundColor Yellow
        Write-Host "You can trigger manually with:" -ForegroundColor Cyan
        Write-Host "Invoke-RestMethod -Uri 'http://localhost:5000/api/retraining/trigger?min_feedback=20' -Method POST" -ForegroundColor Gray
    }
    
} catch {
    Write-Host "Error checking status: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n======================================================================"
Write-Host "DONE"
Write-Host "======================================================================`n"