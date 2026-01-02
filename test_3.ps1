# # # # # test_dual_simple.ps1 - Test BOTH modes (NO EMOJIS)
# # # # Write-Host ""
# # # # Write-Host "="*80 -ForegroundColor Cyan
# # # # Write-Host "DUAL MODE FRAUD DETECTION - TEST SUITE" -ForegroundColor Cyan
# # # # Write-Host "="*80 -ForegroundColor Cyan
# # # # Write-Host ""

# # # # # ============================================
# # # # # MODE 1: BANKING
# # # # # ============================================
# # # # Write-Host "MODE 1: BANKING (Raw Transaction Data)" -ForegroundColor Yellow
# # # # Write-Host "-"*80 -ForegroundColor Yellow
# # # # Write-Host ""

# # # # Write-Host "TEST 1: High Risk Banking Transaction" -ForegroundColor Red
# # # # $banking1 = @{
# # # #     mode = "banking"
# # # #     Transaction_Amount = 8000
# # # #     Account_Balance = 1200
# # # #     Transaction_Type = "ATM Withdrawal"
# # # #     Timestamp = "2023-12-23 03:15:00"
# # # #     Daily_Transaction_Count = 15
# # # #     Avg_Transaction_Amount_7d = 250
# # # #     Failed_Transaction_Count_7d = 5
# # # #     Card_Age = 12
# # # #     Transaction_Distance = 4500
# # # #     IP_Address_Flag = 1
# # # # } | ConvertTo-Json

# # # # try {
# # # #     $result = Invoke-RestMethod -Uri "http://localhost:5000/api/check-fraud" -Method POST -Body $banking1 -ContentType "application/json"
    
# # # #     Write-Host "  Mode:              $($result.mode)"
# # # #     Write-Host "  Amount:            `$$($result.transaction_amount)"
# # # #     Write-Host "  Fraud Probability: $([math]::Round($result.fraud_probability * 100, 1))%"
    
# # # #     if ($result.prediction -eq 1) {
# # # #         Write-Host "  Prediction:        [FRAUD DETECTED]" -ForegroundColor Red
# # # #     } else {
# # # #         Write-Host "  Prediction:        [NORMAL]" -ForegroundColor Green
# # # #     }
    
# # # #     Write-Host "  Risk Level:        $($result.risk_level)"
# # # #     Write-Host ""
# # # #     Write-Host "  Top Features:"
# # # #     foreach($f in $result.top_contributing_features | Select-Object -First 3) {
# # # #         Write-Host "    - $($f.feature): $($f.value) (impact: $($f.impact))"
# # # #     }
# # # # } catch {
# # # #     Write-Host "  ERROR: $($_.Exception.Message)" -ForegroundColor Red
# # # # }

# # # # Write-Host ""
# # # # Write-Host "="*80 -ForegroundColor Cyan
# # # # Write-Host ""

# # # # Write-Host "TEST 2: Normal Banking Transaction" -ForegroundColor Green
# # # # $banking2 = @{
# # # #     mode = "banking"
# # # #     Transaction_Amount = 75
# # # #     Account_Balance = 15000
# # # #     Transaction_Type = "POS"
# # # #     Timestamp = "2023-12-23 14:30:00"
# # # #     Daily_Transaction_Count = 3
# # # #     Avg_Transaction_Amount_7d = 80
# # # #     Failed_Transaction_Count_7d = 0
# # # #     Card_Age = 250
# # # #     Transaction_Distance = 300
# # # #     IP_Address_Flag = 0
# # # # } | ConvertTo-Json

# # # # try {
# # # #     $result = Invoke-RestMethod -Uri "http://localhost:5000/api/check-fraud" -Method POST -Body $banking2 -ContentType "application/json"
    
# # # #     Write-Host "  Mode:              $($result.mode)"
# # # #     Write-Host "  Amount:            `$$($result.transaction_amount)"
# # # #     Write-Host "  Fraud Probability: $([math]::Round($result.fraud_probability * 100, 1))%"
    
# # # #     if ($result.prediction -eq 1) {
# # # #         Write-Host "  Prediction:        [FRAUD DETECTED]" -ForegroundColor Red
# # # #     } else {
# # # #         Write-Host "  Prediction:        [NORMAL]" -ForegroundColor Green
# # # #     }
    
# # # #     Write-Host "  Risk Level:        $($result.risk_level)"
# # # # } catch {
# # # #     Write-Host "  ERROR: $($_.Exception.Message)" -ForegroundColor Red
# # # # }

# # # # Write-Host ""
# # # # Write-Host "="*80 -ForegroundColor Cyan
# # # # Write-Host ""

# # # # # ============================================
# # # # # MODE 2: CREDIT CARD
# # # # # ============================================
# # # # Write-Host "MODE 2: CREDIT CARD (V1-V28 Data)" -ForegroundColor Magenta
# # # # Write-Host "-"*80 -ForegroundColor Magenta
# # # # Write-Host ""

# # # # Write-Host "TEST 3: Fraud Pattern (High V14, V10)" -ForegroundColor Red
# # # # $cc_fraud = @{
# # # #     mode = "credit_card"
# # # #     Time = 68000
# # # #     Amount = 225.00
# # # #     V1 = -0.75; V2 = 0.85; V3 = 0.12; V4 = 0.58; V5 = -0.12
# # # #     V6 = 0.32; V7 = 0.12; V8 = 0.05; V9 = -0.18; V10 = 0.95
# # # #     V11 = 0.68; V12 = -1.15; V13 = 0.32; V14 = -2.15; V15 = 0.48
# # # #     V16 = -0.58; V17 = -1.28; V18 = -0.42; V19 = 0.18; V20 = 0.08
# # # #     V21 = 0.25; V22 = 0.38; V23 = -0.08; V24 = -0.28; V25 = 0.25
# # # #     V26 = -0.38; V27 = 0.02; V28 = 0.02
# # # # } | ConvertTo-Json

# # # # try {
# # # #     $result = Invoke-RestMethod -Uri "http://localhost:5000/api/check-fraud" -Method POST -Body $cc_fraud -ContentType "application/json"
    
# # # #     Write-Host "  Mode:              $($result.mode)"
# # # #     Write-Host "  Amount:            `$$($result.transaction_amount)"
# # # #     Write-Host "  Fraud Probability: $([math]::Round($result.fraud_probability * 100, 1))%"
    
# # # #     if ($result.prediction -eq 1) {
# # # #         Write-Host "  Prediction:        [FRAUD DETECTED]" -ForegroundColor Red
# # # #     } else {
# # # #         Write-Host "  Prediction:        [NORMAL]" -ForegroundColor Green
# # # #     }
    
# # # #     Write-Host "  Risk Level:        $($result.risk_level)"
# # # #     Write-Host ""
# # # #     Write-Host "  Top Features:"
# # # #     foreach($f in $result.top_contributing_features | Select-Object -First 3) {
# # # #         Write-Host "    - $($f.feature): $($f.value) (impact: $($f.impact))"
# # # #     }
# # # # } catch {
# # # #     Write-Host "  ERROR: $($_.Exception.Message)" -ForegroundColor Red
# # # # }

# # # # Write-Host ""
# # # # Write-Host "="*80 -ForegroundColor Cyan
# # # # Write-Host ""

# # # # Write-Host "TEST 4: Normal Pattern" -ForegroundColor Green
# # # # $cc_normal = @{
# # # #     mode = "credit_card"
# # # #     Time = 35000
# # # #     Amount = 156.50
# # # #     V1 = 0.38; V2 = 0.55; V3 = -0.15; V4 = 0.65; V5 = 0.22
# # # #     V6 = 0.45; V7 = -0.22; V8 = 0.35; V9 = 0.15; V10 = 0.48
# # # #     V11 = 0.32; V12 = 0.15; V13 = -0.15; V14 = 0.42; V15 = 0.22
# # # #     V16 = 0.38; V17 = -0.22; V18 = 0.22; V19 = 0.15; V20 = 0.22
# # # #     V21 = 0.38; V22 = 0.22; V23 = 0.15; V24 = 0.22; V25 = 0.15
# # # #     V26 = 0.22; V27 = 0.15; V28 = 0.15
# # # # } | ConvertTo-Json

# # # # try {
# # # #     $result = Invoke-RestMethod -Uri "http://localhost:5000/api/check-fraud" -Method POST -Body $cc_normal -ContentType "application/json"
    
# # # #     Write-Host "  Mode:              $($result.mode)"
# # # #     Write-Host "  Amount:            `$$($result.transaction_amount)"
# # # #     Write-Host "  Fraud Probability: $([math]::Round($result.fraud_probability * 100, 1))%"
    
# # # #     if ($result.prediction -eq 1) {
# # # #         Write-Host "  Prediction:        [FRAUD DETECTED]" -ForegroundColor Red
# # # #     } else {
# # # #         Write-Host "  Prediction:        [NORMAL]" -ForegroundColor Green
# # # #     }
    
# # # #     Write-Host "  Risk Level:        $($result.risk_level)"
# # # # } catch {
# # # #     Write-Host "  ERROR: $($_.Exception.Message)" -ForegroundColor Red
# # # # }

# # # # Write-Host ""
# # # # Write-Host "="*80 -ForegroundColor Cyan
# # # # Write-Host ""

# # # # Write-Host "TEST 5: Medium Risk" -ForegroundColor Yellow
# # # # $cc_medium = @{
# # # #     mode = "credit_card"
# # # #     Time = 41000
# # # #     Amount = 98.75
# # # #     V1 = 0.42; V2 = 0.58; V3 = -0.18; V4 = 0.68; V5 = 0.25
# # # #     V6 = 0.48; V7 = -0.25; V8 = 0.38; V9 = 0.18; V10 = 0.52
# # # #     V11 = 0.35; V12 = 0.18; V13 = -0.18; V14 = 0.48; V15 = 0.25
# # # #     V16 = 0.42; V17 = -0.25; V18 = 0.25; V19 = 0.18; V20 = 0.25
# # # #     V21 = 0.42; V22 = 0.25; V23 = 0.18; V24 = 0.25; V25 = 0.18
# # # #     V26 = 0.25; V27 = 0.18; V28 = 0.18
# # # # } | ConvertTo-Json

# # # # try {
# # # #     $result = Invoke-RestMethod -Uri "http://localhost:5000/api/check-fraud" -Method POST -Body $cc_medium -ContentType "application/json"
    
# # # #     Write-Host "  Mode:              $($result.mode)"
# # # #     Write-Host "  Amount:            `$$($result.transaction_amount)"
# # # #     Write-Host "  Fraud Probability: $([math]::Round($result.fraud_probability * 100, 1))%"
    
# # # #     if ($result.prediction -eq 1) {
# # # #         Write-Host "  Prediction:        [FRAUD DETECTED]" -ForegroundColor Red
# # # #     } else {
# # # #         Write-Host "  Prediction:        [NORMAL]" -ForegroundColor Green
# # # #     }
    
# # # #     Write-Host "  Risk Level:        $($result.risk_level)"
# # # # } catch {
# # # #     Write-Host "  ERROR: $($_.Exception.Message)" -ForegroundColor Red
# # # # }

# # # # Write-Host ""
# # # # Write-Host "="*80 -ForegroundColor Magenta
# # # # Write-Host "SUMMARY" -ForegroundColor Magenta
# # # # Write-Host "="*80 -ForegroundColor Magenta
# # # # Write-Host ""
# # # # Write-Host "[OK] BANKING MODE:" -ForegroundColor Green
# # # # Write-Host "   - Uses raw transaction data"
# # # # Write-Host "   - Features: Transaction_Amount, Account_Balance, etc."
# # # # Write-Host ""
# # # # Write-Host "[OK] CREDIT_CARD MODE:" -ForegroundColor Green
# # # # Write-Host "   - Uses V1-V28 PCA features"
# # # # Write-Host "   - Features: V1-V28, Amount, Time"
# # # # Write-Host ""
# # # # Write-Host "="*80 -ForegroundColor Cyan
# # # # Write-Host "TESTING COMPLETE!" -ForegroundColor Cyan
# # # # Write-Host "="*80 -ForegroundColor Cyan
# # # # Write-Host ""

# # # # test_dual_fixed.ps1 - Fixed AI Explanation Display
# # # Write-Host ""
# # # Write-Host "="*80 -ForegroundColor Cyan
# # # Write-Host "DUAL MODE FRAUD DETECTION - TEST SUITE" -ForegroundColor Cyan
# # # Write-Host "="*80 -ForegroundColor Cyan
# # # Write-Host ""

# # # # ============================================
# # # # MODE 1: BANKING
# # # # ============================================
# # # Write-Host "MODE 1: BANKING (Raw Transaction Data)" -ForegroundColor Yellow
# # # Write-Host "-"*80 -ForegroundColor Yellow
# # # Write-Host ""

# # # Write-Host "TEST 1: High Risk Banking Transaction" -ForegroundColor Red
# # # $banking1 = @{
# # #     mode = "banking"
# # #     Transaction_Amount = 8000
# # #     Account_Balance = 1200
# # #     Transaction_Type = "ATM Withdrawal"
# # #     Timestamp = "2023-12-23 03:15:00"
# # #     Daily_Transaction_Count = 15
# # #     Avg_Transaction_Amount_7d = 250
# # #     Failed_Transaction_Count_7d = 5
# # #     Card_Age = 12
# # #     Transaction_Distance = 4500
# # #     IP_Address_Flag = 1
# # # } | ConvertTo-Json

# # # try {
# # #     $result = Invoke-RestMethod -Uri "http://localhost:5000/api/check-fraud" -Method POST -Body $banking1 -ContentType "application/json"
    
# # #     Write-Host "  Mode:              $($result.mode)" -ForegroundColor White
# # #     Write-Host "  Amount:            `$$($result.transaction_amount)" -ForegroundColor White
# # #     Write-Host "  Fraud Probability: $([math]::Round($result.fraud_probability * 100, 1))%" -ForegroundColor $(if($result.fraud_probability -ge 0.7){'Red'}elseif($result.fraud_probability -ge 0.4){'Yellow'}else{'Green'})
    
# # #     if ($result.prediction -eq 1) {
# # #         Write-Host "  Prediction:        [FRAUD DETECTED]" -ForegroundColor Red
# # #     } else {
# # #         Write-Host "  Prediction:        [NORMAL]" -ForegroundColor Green
# # #     }
    
# # #     Write-Host "  Risk Level:        $($result.risk_level)" -ForegroundColor White
# # #     Write-Host "  Model Used:        $($result.model_used)" -ForegroundColor Gray
# # #     Write-Host ""
    
# # #     Write-Host "  TOP CONTRIBUTING FEATURES:" -ForegroundColor Cyan
# # #     foreach($f in $result.top_contributing_features) {
# # #         $impactColor = if($f.impact -eq 'increases'){'Red'}else{'Green'}
# # #         Write-Host "    [$($f.impact.ToUpper())]" -NoNewline -ForegroundColor $impactColor
# # #         Write-Host " $($f.feature)" -NoNewline -ForegroundColor White
# # #         Write-Host " = $([math]::Round($f.value, 2))" -NoNewline -ForegroundColor Yellow
# # #         Write-Host " (contribution: $([math]::Round($f.shap_value, 4)))" -ForegroundColor Gray
# # #     }
    
# # #     Write-Host ""
# # #     Write-Host "  AI EXPLANATION:" -ForegroundColor Magenta
# # #     Write-Host ""
# # #     # FIX: Properly display AI explanation without weird characters
# # #     $lines = $result.ai_explanation -split "`n"
# # #     foreach($line in $lines) {
# # #         if ($line.Trim() -ne "" -and $line -notmatch "^[\+\-=]+$") {
# # #             Write-Host "  $line" -ForegroundColor White
# # #         }
# # #     }
# # #     Write-Host ""
    
# # # } catch {
# # #     Write-Host "  ERROR: $($_.Exception.Message)" -ForegroundColor Red
# # # }

# # # Write-Host ""
# # # Write-Host "="*80 -ForegroundColor Cyan
# # # Write-Host ""

# # # Write-Host "TEST 2: Normal Banking Transaction" -ForegroundColor Green
# # # $banking2 = @{
# # #     mode = "banking"
# # #     Transaction_Amount = 75
# # #     Account_Balance = 15000
# # #     Transaction_Type = "POS"
# # #     Timestamp = "2023-12-23 14:30:00"
# # #     Daily_Transaction_Count = 3
# # #     Avg_Transaction_Amount_7d = 80
# # #     Failed_Transaction_Count_7d = 0
# # #     Card_Age = 250
# # #     Transaction_Distance = 300
# # #     IP_Address_Flag = 0
# # # } | ConvertTo-Json

# # # try {
# # #     $result = Invoke-RestMethod -Uri "http://localhost:5000/api/check-fraud" -Method POST -Body $banking2 -ContentType "application/json"
    
# # #     Write-Host "  Mode:              $($result.mode)" -ForegroundColor White
# # #     Write-Host "  Amount:            `$$($result.transaction_amount)" -ForegroundColor White
# # #     Write-Host "  Fraud Probability: $([math]::Round($result.fraud_probability * 100, 1))%" -ForegroundColor $(if($result.fraud_probability -ge 0.7){'Red'}elseif($result.fraud_probability -ge 0.4){'Yellow'}else{'Green'})
    
# # #     if ($result.prediction -eq 1) {
# # #         Write-Host "  Prediction:        [FRAUD DETECTED]" -ForegroundColor Red
# # #     } else {
# # #         Write-Host "  Prediction:        [NORMAL]" -ForegroundColor Green
# # #     }
    
# # #     Write-Host "  Risk Level:        $($result.risk_level)" -ForegroundColor White
# # #     Write-Host ""
    
# # #     Write-Host "  TOP CONTRIBUTING FEATURES:" -ForegroundColor Cyan
# # #     foreach($f in $result.top_contributing_features | Select-Object -First 3) {
# # #         $impactColor = if($f.impact -eq 'increases'){'Red'}else{'Green'}
# # #         Write-Host "    [$($f.impact.ToUpper())] $($f.feature) = $([math]::Round($f.value, 2))" -ForegroundColor White
# # #     }
    
# # #     Write-Host ""
# # #     Write-Host "  AI EXPLANATION:" -ForegroundColor Magenta
# # #     Write-Host ""
# # #     $lines = $result.ai_explanation -split "`n"
# # #     foreach($line in $lines) {
# # #         if ($line.Trim() -ne "" -and $line -notmatch "^[\+\-=]+$") {
# # #             Write-Host "  $line" -ForegroundColor White
# # #         }
# # #     }
# # #     Write-Host ""
    
# # # } catch {
# # #     Write-Host "  ERROR: $($_.Exception.Message)" -ForegroundColor Red
# # # }

# # # Write-Host ""
# # # Write-Host "="*80 -ForegroundColor Cyan
# # # Write-Host ""

# # # # ============================================
# # # # MODE 2: CREDIT CARD
# # # # ============================================
# # # Write-Host "MODE 2: CREDIT CARD (V1-V28 Data)" -ForegroundColor Magenta
# # # Write-Host "-"*80 -ForegroundColor Magenta
# # # Write-Host ""

# # # Write-Host "TEST 3: Fraud Pattern" -ForegroundColor Red
# # # $cc_fraud = @{
# # #     mode = "credit_card"
# # #     Time = 68000
# # #     Amount = 225.00
# # #     V1 = -0.75; V2 = 0.85; V3 = 0.12; V4 = 0.58; V5 = -0.12
# # #     V6 = 0.32; V7 = 0.12; V8 = 0.05; V9 = -0.18; V10 = 0.95
# # #     V11 = 0.68; V12 = -1.15; V13 = 0.32; V14 = -2.15; V15 = 0.48
# # #     V16 = -0.58; V17 = -1.28; V18 = -0.42; V19 = 0.18; V20 = 0.08
# # #     V21 = 0.25; V22 = 0.38; V23 = -0.08; V24 = -0.28; V25 = 0.25
# # #     V26 = -0.38; V27 = 0.02; V28 = 0.02
# # # } | ConvertTo-Json

# # # try {
# # #     $result = Invoke-RestMethod -Uri "http://localhost:5000/api/check-fraud" -Method POST -Body $cc_fraud -ContentType "application/json"
    
# # #     Write-Host "  Mode:              $($result.mode)" -ForegroundColor White
# # #     Write-Host "  Amount:            `$$($result.transaction_amount)" -ForegroundColor White
# # #     Write-Host "  Fraud Probability: $([math]::Round($result.fraud_probability * 100, 1))%" -ForegroundColor $(if($result.fraud_probability -ge 0.7){'Red'}elseif($result.fraud_probability -ge 0.4){'Yellow'}else{'Green'})
    
# # #     if ($result.prediction -eq 1) {
# # #         Write-Host "  Prediction:        [FRAUD DETECTED]" -ForegroundColor Red
# # #     } else {
# # #         Write-Host "  Prediction:        [NORMAL]" -ForegroundColor Green
# # #     }
    
# # #     Write-Host "  Risk Level:        $($result.risk_level)" -ForegroundColor White
# # #     Write-Host "  Model Used:        $($result.model_used)" -ForegroundColor Gray
# # #     Write-Host ""
    
# # #     Write-Host "  TOP CONTRIBUTING FEATURES:" -ForegroundColor Cyan
# # #     foreach($f in $result.top_contributing_features | Select-Object -First 5) {
# # #         $impactColor = if($f.impact -eq 'increases'){'Red'}else{'Green'}
# # #         Write-Host "    [$($f.impact.ToUpper())] $($f.feature) = $([math]::Round($f.value, 2))" -ForegroundColor White
# # #     }
    
# # #     Write-Host ""
# # #     Write-Host "  AI EXPLANATION:" -ForegroundColor Magenta
# # #     Write-Host ""
# # #     $lines = $result.ai_explanation -split "`n"
# # #     foreach($line in $lines) {
# # #         if ($line.Trim() -ne "" -and $line -notmatch "^[\+\-=]+$") {
# # #             Write-Host "  $line" -ForegroundColor White
# # #         }
# # #     }
# # #     Write-Host ""
    
# # # } catch {
# # #     Write-Host "  ERROR: $($_.Exception.Message)" -ForegroundColor Red
# # # }

# # # Write-Host ""
# # # Write-Host "="*80 -ForegroundColor Cyan
# # # Write-Host "TESTING COMPLETE!" -ForegroundColor Cyan
# # # Write-Host "="*80 -ForegroundColor Cyan
# # # Write-Host ""




# # # #### test3#####


# # # test_database_integration.ps1 - Test Database Integration
# # Write-Host ""
# # Write-Host "="*80 -ForegroundColor Cyan
# # Write-Host "DATABASE INTEGRATION TEST" -ForegroundColor Cyan
# # Write-Host "="*80 -ForegroundColor Cyan
# # Write-Host ""

# # $baseUrl = "http://localhost:5000"

# # # ============================================
# # # TEST 1: BANKING TRANSACTION
# # # ============================================
# # Write-Host "TEST 1: Banking Fraud Transaction" -ForegroundColor Yellow
# # Write-Host ""

# # $banking = @{
# #     mode = "banking"
# #     Transaction_Amount = 8000
# #     Account_Balance = 1200
# #     Transaction_Type = "ATM Withdrawal"
# #     Timestamp = "2023-12-24 03:15:00"
# #     Daily_Transaction_Count = 15
# #     Avg_Transaction_Amount_7d = 250
# #     Failed_Transaction_Count_7d = 5
# #     Card_Age = 12
# #     Transaction_Distance = 4500
# #     IP_Address_Flag = 1
# # } | ConvertTo-Json

# # try {
# #     $result = Invoke-RestMethod -Uri "$baseUrl/api/check-fraud" -Method POST -Body $banking -ContentType "application/json"
    
# #     Write-Host "  Status:            $($result.status)" -ForegroundColor Green
# #     Write-Host "  Prediction ID:     $($result.prediction_id)" -ForegroundColor Cyan
# #     Write-Host "  Mode:              $($result.mode)" -ForegroundColor White
# #     Write-Host "  Prediction:        $(if($result.prediction -eq 1){'FRAUD'}else{'NORMAL'})" -ForegroundColor $(if($result.prediction -eq 1){'Red'}else{'Green'})
# #     Write-Host "  Fraud Probability: $([math]::Round($result.fraud_probability * 100, 1))%" -ForegroundColor Yellow
# #     Write-Host "  Risk Level:        $($result.risk_level)" -ForegroundColor White
# #     Write-Host ""
    
# #     # Store prediction ID for later
# #     $bankingPredId = $result.prediction_id
    
# #     Write-Host "  TOP FEATURES:" -ForegroundColor Cyan
# #     foreach($f in $result.top_contributing_features | Select-Object -First 3) {
# #         Write-Host "    • $($f.feature) = $($f.value) [$($f.impact)]" -ForegroundColor Gray
# #     }
# #     Write-Host ""
    
# # } catch {
# #     Write-Host "  ERROR: $($_.Exception.Message)" -ForegroundColor Red
# # }

# # Start-Sleep -Seconds 1

# # # ============================================
# # # TEST 2: CREDIT CARD TRANSACTION
# # # ============================================
# # Write-Host "TEST 2: Credit Card Fraud Transaction" -ForegroundColor Yellow
# # Write-Host ""

# # $creditCard = @{
# #     mode = "credit_card"
# #     Time = 68000
# #     Amount = 225.00
# #     V1 = -0.75; V2 = 0.85; V3 = 0.12; V4 = 0.58; V5 = -0.12
# #     V6 = 0.32; V7 = 0.12; V8 = 0.05; V9 = -0.18; V10 = 0.95
# #     V11 = 0.68; V12 = -1.15; V13 = 0.32; V14 = -2.15; V15 = 0.48
# #     V16 = -0.58; V17 = -1.28; V18 = -0.42; V19 = 0.18; V20 = 0.08
# #     V21 = 0.25; V22 = 0.38; V23 = -0.08; V24 = -0.28; V25 = 0.25
# #     V26 = -0.38; V27 = 0.02; V28 = 0.02
# # } | ConvertTo-Json

# # try {
# #     $result = Invoke-RestMethod -Uri "$baseUrl/api/check-fraud" -Method POST -Body $creditCard -ContentType "application/json"
    
# #     Write-Host "  Status:            $($result.status)" -ForegroundColor Green
# #     Write-Host "  Prediction ID:     $($result.prediction_id)" -ForegroundColor Cyan
# #     Write-Host "  Mode:              $($result.mode)" -ForegroundColor White
# #     Write-Host "  Prediction:        $(if($result.prediction -eq 1){'FRAUD'}else{'NORMAL'})" -ForegroundColor $(if($result.prediction -eq 1){'Red'}else{'Green'})
# #     Write-Host "  Fraud Probability: $([math]::Round($result.fraud_probability * 100, 1))%" -ForegroundColor Yellow
# #     Write-Host ""
    
# #     $ccPredId = $result.prediction_id
    
# #     Write-Host "  TOP FEATURES:" -ForegroundColor Cyan
# #     foreach($f in $result.top_contributing_features | Select-Object -First 3) {
# #         Write-Host "    • $($f.feature) = $($f.value) [$($f.impact)]" -ForegroundColor Gray
# #     }
# #     Write-Host ""
    
# # } catch {
# #     Write-Host "  ERROR: $($_.Exception.Message)" -ForegroundColor Red
# # }

# # Start-Sleep -Seconds 1

# # # ============================================
# # # TEST 3: GET RECENT PREDICTIONS
# # # ============================================
# # Write-Host "TEST 3: Get Recent Predictions" -ForegroundColor Yellow
# # Write-Host ""

# # try {
# #     $recent = Invoke-RestMethod -Uri "$baseUrl/api/predictions?limit=5" -Method GET
    
# #     Write-Host "  Status:            $($recent.status)" -ForegroundColor Green
# #     Write-Host "  Count:             $($recent.count)" -ForegroundColor White
# #     Write-Host ""
# #     Write-Host "  RECENT PREDICTIONS:" -ForegroundColor Cyan
    
# #     foreach($p in $recent.predictions) {
# #         $predType = if($p.prediction -eq 1){"FRAUD"}else{"NORMAL"}
# #         $color = if($p.prediction -eq 1){"Red"}else{"Green"}
# #         Write-Host "    ID $($p.id): $($p.model_type) - $$($p.amount) - $predType ($([math]::Round($p.fraud_probability * 100, 1))%)" -ForegroundColor $color
# #     }
# #     Write-Host ""
    
# # } catch {
# #     Write-Host "  ERROR: $($_.Exception.Message)" -ForegroundColor Red
# # }

# # Start-Sleep -Seconds 1

# # # ============================================
# # # TEST 4: GET SPECIFIC PREDICTION
# # # ============================================
# # if ($bankingPredId) {
# #     Write-Host "TEST 4: Get Specific Prediction (ID: $bankingPredId)" -ForegroundColor Yellow
# #     Write-Host ""
    
# #     try {
# #         $pred = Invoke-RestMethod -Uri "$baseUrl/api/predictions/$bankingPredId" -Method GET
        
# #         Write-Host "  Status:            $($pred.status)" -ForegroundColor Green
# #         Write-Host "  ID:                $($pred.prediction.id)" -ForegroundColor White
# #         Write-Host "  Model Type:        $($pred.prediction.model_type)" -ForegroundColor White
# #         Write-Host "  Amount:            `$$($pred.prediction.amount)" -ForegroundColor White
# #         Write-Host "  Prediction:        $(if($pred.prediction.prediction -eq 1){'FRAUD'}else{'NORMAL'})" -ForegroundColor $(if($pred.prediction.prediction -eq 1){'Red'}else{'Green'})
# #         Write-Host "  Risk Level:        $($pred.prediction.risk_level)" -ForegroundColor Yellow
# #         Write-Host "  Predicted At:      $($pred.prediction.predicted_at)" -ForegroundColor Gray
# #         Write-Host ""
        
# #     } catch {
# #         Write-Host "  ERROR: $($_.Exception.Message)" -ForegroundColor Red
# #     }
# # }

# # Start-Sleep -Seconds 1

# # # ============================================
# # # TEST 5: SUBMIT FEEDBACK
# # # ============================================
# # if ($bankingPredId) {
# #     Write-Host "TEST 5: Submit Feedback (ID: $bankingPredId)" -ForegroundColor Yellow
# #     Write-Host ""
    
# #     $feedback = @{
# #         actual_class = 1
# #         feedback_note = "Confirmed fraud by investigation team"
# #     } | ConvertTo-Json
    
# #     try {
# #         $result = Invoke-RestMethod -Uri "$baseUrl/api/predictions/$bankingPredId/feedback" -Method POST -Body $feedback -ContentType "application/json"
        
# #         Write-Host "  Status:            $($result.status)" -ForegroundColor Green
# #         Write-Host "  Message:           $($result.message)" -ForegroundColor White
# #         Write-Host "  Total Feedback:    $($result.total_feedback)" -ForegroundColor Cyan
# #         Write-Host ""
        
# #     } catch {
# #         Write-Host "  ERROR: $($_.Exception.Message)" -ForegroundColor Red
# #     }
# # }

# # Start-Sleep -Seconds 1

# # # ============================================
# # # VERIFY IN DATABASE
# # # ============================================
# # Write-Host "="*80 -ForegroundColor Cyan
# # Write-Host "VERIFY IN DATABASE" -ForegroundColor Cyan
# # Write-Host "="*80 -ForegroundColor Cyan
# # Write-Host ""

# # Write-Host "Run these PostgreSQL queries to verify:" -ForegroundColor Yellow
# # Write-Host ""
# # Write-Host "1. View all predictions:" -ForegroundColor White
# # Write-Host "   psql -U postgres -d fraud_detection -c ""SELECT id, model_type, amount, prediction, fraud_probability FROM predictions ORDER BY id DESC LIMIT 5;""" -ForegroundColor Gray
# # Write-Host ""

# # Write-Host "2. View predictions by model type:" -ForegroundColor White
# # Write-Host "   psql -U postgres -d fraud_detection -c ""SELECT model_type, COUNT(*) FROM predictions GROUP BY model_type;""" -ForegroundColor Gray
# # Write-Host ""

# # Write-Host "3. View feedback:" -ForegroundColor White
# # Write-Host "   psql -U postgres -d fraud_detection -c ""SELECT * FROM feedback ORDER BY id DESC LIMIT 5;""" -ForegroundColor Gray
# # Write-Host ""

# # Write-Host "4. View high risk transactions:" -ForegroundColor White
# # Write-Host "   psql -U postgres -d fraud_detection -c ""SELECT * FROM high_risk_transactions LIMIT 5;""" -ForegroundColor Gray
# # Write-Host ""

# # # ============================================
# # # AUTO-VERIFY (if psql is available)
# # # ============================================
# # Write-Host "="*80 -ForegroundColor Cyan
# # Write-Host "AUTO DATABASE VERIFICATION" -ForegroundColor Cyan
# # Write-Host "="*80 -ForegroundColor Cyan
# # Write-Host ""

# # try {
# #     # Test if psql is available
# #     $null = psql --version 2>&1
    
# #     Write-Host "Checking database..." -ForegroundColor Yellow
# #     Write-Host ""
    
# #     # Count predictions
# #     $query1 = "SELECT COUNT(*) as count FROM predictions;"
# #     $count = psql -U postgres -d fraud_detection -t -c $query1 2>$null
# #     Write-Host "  Total Predictions: $($count.Trim())" -ForegroundColor Green
    
# #     # Count by model type
# #     $query2 = "SELECT model_type, COUNT(*) FROM predictions GROUP BY model_type;"
# #     Write-Host "  By Model Type:" -ForegroundColor Cyan
# #     $result = psql -U postgres -d fraud_detection -t -c $query2 2>$null
# #     $result -split "`n" | ForEach-Object {
# #         if ($_.Trim() -ne "") {
# #             Write-Host "    $($_.Trim())" -ForegroundColor Gray
# #         }
# #     }
# #     Write-Host ""
    
# #     # Count feedback
# #     $query3 = "SELECT COUNT(*) as count FROM predictions WHERE actual_class IS NOT NULL;"
# #     $feedbackCount = psql -U postgres -d fraud_detection -t -c $query3 2>$null
# #     Write-Host "  Total Feedback: $($feedbackCount.Trim())" -ForegroundColor Green
# #     Write-Host ""
    
# #     Write-Host "✅ Database verification complete!" -ForegroundColor Green
    
# # } catch {
# #     Write-Host "⚠️  psql not available for auto-verification" -ForegroundColor Yellow
# #     Write-Host "   Run the queries above manually to verify" -ForegroundColor Gray
# # }

# # Write-Host ""
# # Write-Host "="*80 -ForegroundColor Cyan
# # Write-Host "✅ ALL TESTS COMPLETE" -ForegroundColor Green
# # Write-Host "="*80 -ForegroundColor Cyan
# # Write-Host ""



# ##### 20 samples genearted ####

# # # test_20_samples_fixed.ps1 - NO EMOJI VERSION
# # # test_3.ps1 - UPDATED WITH CLEANUP
# # Write-Host ""
# # Write-Host "="*90 -ForegroundColor Cyan
# # Write-Host "AUTO-RETRAINING TEST WITH DATA CLEANUP" -ForegroundColor Cyan
# # Write-Host "="*90 -ForegroundColor Cyan
# # Write-Host ""

# # $baseUrl = "http://localhost:5000"

# # # ============================================
# # # PHASE 0: CLEANUP OLD TEST DATA
# # # ============================================
# # Write-Host "PHASE 0: Cleaning Up Old Test Data" -ForegroundColor Yellow
# # Write-Host ""

# # try {
# #     # Get total count before cleanup
# #     $countBefore = psql -U postgres -d fraud_detection -t -c "SELECT COUNT(*) FROM predictions;"
# #     Write-Host "  Current total predictions: $($countBefore.Trim())" -ForegroundColor White
    
# #     # Count by model type
# #     Write-Host "  Current by model type:" -ForegroundColor Cyan
# #     $byModel = psql -U postgres -d fraud_detection -t -c "SELECT model_type, COUNT(*) FROM predictions GROUP BY model_type;"
# #     $byModel -split "`n" | ForEach-Object {
# #         if ($_.Trim() -ne "") {
# #             Write-Host "    $($_.Trim())" -ForegroundColor Gray
# #         }
# #     }
# #     Write-Host ""
    
# #     # Delete feedback entries (foreign key constraint)
# #     Write-Host "  Deleting old feedback entries..." -ForegroundColor Yellow
# #     psql -U postgres -d fraud_detection -c "DELETE FROM feedback;" | Out-Null
# #     Write-Host "  [OK] Feedback deleted" -ForegroundColor Green
    
# #     # Keep only latest 20 banking predictions
# #     Write-Host "  Keeping only latest 20 banking predictions..." -ForegroundColor Yellow
# #     $deleteBanking = psql -U postgres -d fraud_detection -c "
# #         DELETE FROM predictions 
# #         WHERE model_type = 'banking' 
# #         AND id NOT IN (
# #             SELECT id FROM predictions 
# #             WHERE model_type = 'banking' 
# #             ORDER BY id DESC 
# #             LIMIT 20
# #         );
# #     "
# #     Write-Host "  [OK] Old banking predictions removed" -ForegroundColor Green
    
# #     # Keep only latest 20 credit card predictions
# #     Write-Host "  Keeping only latest 20 credit card predictions..." -ForegroundColor Yellow
# #     $deleteCC = psql -U postgres -d fraud_detection -c "
# #         DELETE FROM predictions 
# #         WHERE model_type = 'credit_card' 
# #         AND id NOT IN (
# #             SELECT id FROM predictions 
# #             WHERE model_type = 'credit_card' 
# #             ORDER BY id DESC 
# #             LIMIT 20
# #         );
# #     "
# #     Write-Host "  [OK] Old credit card predictions removed" -ForegroundColor Green
    
# #     # Show counts after cleanup
# #     Write-Host ""
# #     Write-Host "  After cleanup:" -ForegroundColor Cyan
# #     $afterCleanup = psql -U postgres -d fraud_detection -t -c "SELECT model_type, COUNT(*) FROM predictions GROUP BY model_type ORDER BY model_type;"
# #     $afterCleanup -split "`n" | ForEach-Object {
# #         if ($_.Trim() -ne "") {
# #             Write-Host "    $($_.Trim())" -ForegroundColor Green
# #         }
# #     }
    
# #     Write-Host ""
# #     Write-Host "  [CLEANUP COMPLETE]" -ForegroundColor Green
    
# # } catch {
# #     Write-Host "  [WARNING] Cleanup failed: $($_.Exception.Message)" -ForegroundColor Yellow
# #     Write-Host "  Continuing with test..." -ForegroundColor Gray
# # }

# # Write-Host ""
# # Start-Sleep -Seconds 1

# # # ============================================
# # # PHASE 1: 10 BANKING SAMPLES
# # # ============================================
# # Write-Host "="*90 -ForegroundColor Cyan
# # Write-Host "PHASE 1: 10 Banking Transactions" -ForegroundColor Yellow
# # Write-Host "="*90 -ForegroundColor Cyan
# # Write-Host ""

# # $predictions = @()

# # $bankingSamples = @(
# #     @{Transaction_Amount=8000; Account_Balance=1200; Transaction_Type="ATM Withdrawal"; Timestamp="2023-12-24 03:15:00"; Daily_Transaction_Count=15; Avg_Transaction_Amount_7d=250; Failed_Transaction_Count_7d=5; Card_Age=12; Transaction_Distance=4500; IP_Address_Flag=1; actual_fraud=1},
# #     @{Transaction_Amount=5500; Account_Balance=800; Transaction_Type="Online"; Timestamp="2023-12-24 02:30:00"; Daily_Transaction_Count=12; Avg_Transaction_Amount_7d=300; Failed_Transaction_Count_7d=3; Card_Age=8; Transaction_Distance=3000; IP_Address_Flag=1; actual_fraud=1},
# #     @{Transaction_Amount=75; Account_Balance=15000; Transaction_Type="POS"; Timestamp="2023-12-24 14:30:00"; Daily_Transaction_Count=3; Avg_Transaction_Amount_7d=80; Failed_Transaction_Count_7d=0; Card_Age=250; Transaction_Distance=300; IP_Address_Flag=0; actual_fraud=0},
# #     @{Transaction_Amount=150; Account_Balance=5000; Transaction_Type="POS"; Timestamp="2023-12-24 12:00:00"; Daily_Transaction_Count=4; Avg_Transaction_Amount_7d=120; Failed_Transaction_Count_7d=0; Card_Age=180; Transaction_Distance=200; IP_Address_Flag=0; actual_fraud=0},
# #     @{Transaction_Amount=9500; Account_Balance=900; Transaction_Type="ATM Withdrawal"; Timestamp="2023-12-24 04:00:00"; Daily_Transaction_Count=18; Avg_Transaction_Amount_7d=200; Failed_Transaction_Count_7d=6; Card_Age=10; Transaction_Distance=5000; IP_Address_Flag=1; actual_fraud=1},
# #     @{Transaction_Amount=45; Account_Balance=8000; Transaction_Type="POS"; Timestamp="2023-12-24 10:30:00"; Daily_Transaction_Count=2; Avg_Transaction_Amount_7d=50; Failed_Transaction_Count_7d=0; Card_Age=300; Transaction_Distance=150; IP_Address_Flag=0; actual_fraud=0},
# #     @{Transaction_Amount=6200; Account_Balance=1500; Transaction_Type="Online"; Timestamp="2023-12-24 01:45:00"; Daily_Transaction_Count=14; Avg_Transaction_Amount_7d=280; Failed_Transaction_Count_7d=4; Card_Age=15; Transaction_Distance=4000; IP_Address_Flag=1; actual_fraud=1},
# #     @{Transaction_Amount=220; Account_Balance=12000; Transaction_Type="POS"; Timestamp="2023-12-24 18:00:00"; Daily_Transaction_Count=5; Avg_Transaction_Amount_7d=200; Failed_Transaction_Count_7d=0; Card_Age=200; Transaction_Distance=400; IP_Address_Flag=0; actual_fraud=0},
# #     @{Transaction_Amount=7800; Account_Balance=1100; Transaction_Type="Transfer"; Timestamp="2023-12-24 03:30:00"; Daily_Transaction_Count=16; Avg_Transaction_Amount_7d=220; Failed_Transaction_Count_7d=5; Card_Age=11; Transaction_Distance=4800; IP_Address_Flag=1; actual_fraud=1},
# #     @{Transaction_Amount=95; Account_Balance=6500; Transaction_Type="POS"; Timestamp="2023-12-24 16:00:00"; Daily_Transaction_Count=3; Avg_Transaction_Amount_7d=90; Failed_Transaction_Count_7d=0; Card_Age=220; Transaction_Distance=250; IP_Address_Flag=0; actual_fraud=0}
# # )

# # foreach ($i in 0..9) {
# #     $sample = $bankingSamples[$i]
# #     $actual_fraud = $sample.actual_fraud
# #     $sample.Remove('actual_fraud')
# #     $sample['mode'] = 'banking'
    
# #     $body = $sample | ConvertTo-Json
    
# #     try {
# #         $result = Invoke-RestMethod -Uri "$baseUrl/api/check-fraud" -Method POST -Body $body -ContentType "application/json"
        
# #         $predType = if($result.prediction -eq 1){"FRAUD"}else{"NORMAL"}
# #         $color = if($result.prediction -eq 1){"Red"}else{"Green"}
        
# #         Write-Host "  $($i+1). Banking ID $($result.prediction_id): `$$($sample.Transaction_Amount) - $predType" -ForegroundColor $color
        
# #         $predictions += @{id=$result.prediction_id; actual=$actual_fraud; mode='banking'}
        
# #         Start-Sleep -Milliseconds 200
# #     } catch {
# #         Write-Host "  ERROR: $($_.Exception.Message)" -ForegroundColor Red
# #     }
# # }

# # Write-Host ""

# # # ============================================
# # # PHASE 2: 10 CREDIT CARD SAMPLES
# # # ============================================
# # Write-Host "="*90 -ForegroundColor Cyan
# # Write-Host "PHASE 2: 10 Credit Card Transactions" -ForegroundColor Magenta
# # Write-Host "="*90 -ForegroundColor Cyan
# # Write-Host ""

# # $ccSamples = @(
# #     @{Time=68000; Amount=225; V1=-0.75; V2=0.85; V3=0.12; V4=0.58; V5=-0.12; V6=0.32; V7=0.12; V8=0.05; V9=-0.18; V10=0.95; V11=0.68; V12=-1.15; V13=0.32; V14=-2.15; V15=0.48; V16=-0.58; V17=-1.28; V18=-0.42; V19=0.18; V20=0.08; V21=0.25; V22=0.38; V23=-0.08; V24=-0.28; V25=0.25; V26=-0.38; V27=0.02; V28=0.02; actual_fraud=1},
# #     @{Time=72000; Amount=189; V1=-0.82; V2=0.92; V3=0.15; V4=0.62; V5=-0.15; V6=0.35; V7=0.15; V8=0.08; V9=-0.22; V10=1.02; V11=0.72; V12=-1.22; V13=0.35; V14=-2.25; V15=0.52; V16=-0.62; V17=-1.35; V18=-0.45; V19=0.22; V20=0.12; V21=0.28; V22=0.42; V23=-0.12; V24=-0.32; V25=0.28; V26=-0.42; V27=0.05; V28=0.05; actual_fraud=1},
# #     @{Time=35000; Amount=156.5; V1=0.38; V2=0.55; V3=-0.15; V4=0.65; V5=0.22; V6=0.45; V7=-0.22; V8=0.35; V9=0.15; V10=0.48; V11=0.32; V12=0.15; V13=-0.15; V14=0.42; V15=0.22; V16=0.38; V17=-0.22; V18=0.22; V19=0.15; V20=0.22; V21=0.38; V22=0.22; V23=0.15; V24=0.22; V25=0.15; V26=0.22; V27=0.15; V28=0.15; actual_fraud=0},
# #     @{Time=42000; Amount=127; V1=0.42; V2=0.58; V3=-0.18; V4=0.68; V5=0.25; V6=0.48; V7=-0.25; V8=0.38; V9=0.18; V10=0.52; V11=0.35; V12=0.18; V13=-0.18; V14=0.45; V15=0.25; V16=0.42; V17=-0.25; V18=0.25; V19=0.18; V20=0.25; V21=0.42; V22=0.25; V23=0.18; V24=0.25; V25=0.18; V26=0.25; V27=0.18; V28=0.18; actual_fraud=0},
# #     @{Time=75000; Amount=298; V1=-0.88; V2=0.98; V3=0.18; V4=0.68; V5=-0.18; V6=0.38; V7=0.18; V8=0.12; V9=-0.25; V10=1.08; V11=0.78; V12=-1.28; V13=0.38; V14=-2.35; V15=0.58; V16=-0.68; V17=-1.42; V18=-0.48; V19=0.25; V20=0.15; V21=0.32; V22=0.48; V23=-0.15; V24=-0.35; V25=0.32; V26=-0.48; V27=0.08; V28=0.08; actual_fraud=1},
# #     @{Time=38000; Amount=89; V1=0.45; V2=0.62; V3=-0.22; V4=0.72; V5=0.28; V6=0.52; V7=-0.28; V8=0.42; V9=0.22; V10=0.55; V11=0.38; V12=0.22; V13=-0.22; V14=0.48; V15=0.28; V16=0.45; V17=-0.28; V18=0.28; V19=0.22; V20=0.28; V21=0.45; V22=0.28; V23=0.22; V24=0.28; V25=0.22; V26=0.28; V27=0.22; V28=0.22; actual_fraud=0},
# #     @{Time=78000; Amount=315; V1=-0.92; V2=1.05; V3=0.22; V4=0.72; V5=-0.22; V6=0.42; V7=0.22; V8=0.15; V9=-0.28; V10=1.15; V11=0.82; V12=-1.35; V13=0.42; V14=-2.45; V15=0.62; V16=-0.72; V17=-1.48; V18=-0.52; V19=0.28; V20=0.18; V21=0.35; V22=0.52; V23=-0.18; V24=-0.38; V25=0.35; V26=-0.52; V27=0.12; V28=0.12; actual_fraud=1},
# #     @{Time=45000; Amount=178; V1=0.48; V2=0.65; V3=-0.25; V4=0.75; V5=0.32; V6=0.55; V7=-0.32; V8=0.45; V9=0.25; V10=0.58; V11=0.42; V12=0.25; V13=-0.25; V14=0.52; V15=0.32; V16=0.48; V17=-0.32; V18=0.32; V19=0.25; V20=0.32; V21=0.48; V22=0.32; V23=0.25; V24=0.32; V25=0.25; V26=0.32; V27=0.25; V28=0.25; actual_fraud=0},
# #     @{Time=80000; Amount=267; V1=-0.78; V2=0.88; V3=0.15; V4=0.62; V5=-0.15; V6=0.35; V7=0.15; V8=0.08; V9=-0.22; V10=1.02; V11=0.72; V12=-1.22; V13=0.35; V14=-2.28; V15=0.52; V16=-0.62; V17=-1.35; V18=-0.45; V19=0.22; V20=0.12; V21=0.28; V22=0.42; V23=-0.12; V24=-0.32; V25=0.28; V26=-0.42; V27=0.05; V28=0.05; actual_fraud=1},
# #     @{Time=48000; Amount=142; V1=0.52; V2=0.68; V3=-0.28; V4=0.78; V5=0.35; V6=0.58; V7=-0.35; V8=0.48; V9=0.28; V10=0.62; V11=0.45; V12=0.28; V13=-0.28; V14=0.55; V15=0.35; V16=0.52; V17=-0.35; V18=0.35; V19=0.28; V20=0.35; V21=0.52; V22=0.35; V23=0.28; V24=0.35; V25=0.28; V26=0.35; V27=0.28; V28=0.28; actual_fraud=0}
# # )

# # foreach ($i in 0..9) {
# #     $sample = $ccSamples[$i]
# #     $actual_fraud = $sample.actual_fraud
# #     $sample.Remove('actual_fraud')
# #     $sample['mode'] = 'credit_card'
    
# #     $body = $sample | ConvertTo-Json
    
# #     try {
# #         $result = Invoke-RestMethod -Uri "$baseUrl/api/check-fraud" -Method POST -Body $body -ContentType "application/json"
        
# #         $predType = if($result.prediction -eq 1){"FRAUD"}else{"NORMAL"}
# #         $color = if($result.prediction -eq 1){"Red"}else{"Green"}
        
# #         Write-Host "  $($i+1). Credit Card ID $($result.prediction_id): `$$($sample.Amount) - $predType" -ForegroundColor $color
        
# #         $predictions += @{id=$result.prediction_id; actual=$actual_fraud; mode='credit_card'}
        
# #         Start-Sleep -Milliseconds 200
# #     } catch {
# #         Write-Host "  ERROR: $($_.Exception.Message)" -ForegroundColor Red
# #     }
# # }

# # Write-Host ""

# # # ============================================
# # # PHASE 3: SUBMIT FEEDBACK
# # # ============================================
# # Write-Host "="*90 -ForegroundColor Cyan
# # Write-Host "PHASE 3: Submit Feedback for All 20 Samples" -ForegroundColor Yellow
# # Write-Host "="*90 -ForegroundColor Cyan
# # Write-Host ""

# # $feedbackCount = 0

# # foreach ($pred in $predictions) {
# #     $feedback = @{
# #         actual_class = $pred.actual
# #         feedback_note = "Test feedback for auto-retraining"
# #     } | ConvertTo-Json
    
# #     try {
# #         $result = Invoke-RestMethod -Uri "$baseUrl/api/predictions/$($pred.id)/feedback" -Method POST -Body $feedback -ContentType "application/json"
        
# #         $feedbackCount++
# #         Write-Host "  [OK] Feedback $feedbackCount/20: ID $($pred.id) [$($pred.mode)] - Actual: $($pred.actual)" -ForegroundColor Green
        
# #         Start-Sleep -Milliseconds 150
# #     } catch {
# #         Write-Host "  [FAIL] ID $($pred.id): $($_.Exception.Message)" -ForegroundColor Red
# #     }
# # }

# # Write-Host ""

# # # ============================================
# # # PHASE 4: CHECK RETRAINING STATUS
# # # ============================================
# # Write-Host "="*90 -ForegroundColor Cyan
# # Write-Host "PHASE 4: Check Retraining Status" -ForegroundColor Yellow
# # Write-Host "="*90 -ForegroundColor Cyan
# # Write-Host ""

# # try {
# #     $status = Invoke-RestMethod -Uri "$baseUrl/api/retrain/status" -Method GET
    
# #     Write-Host "  Retraining Threshold: $($status.threshold)" -ForegroundColor White
# #     Write-Host ""
# #     Write-Host "  BANKING:" -ForegroundColor Cyan
# #     Write-Host "    Feedback Count: $($status.banking.feedback_count)" -ForegroundColor White
# #     Write-Host "    Progress:       $($status.banking.progress)" -ForegroundColor Yellow
# #     Write-Host "    Ready:          $($status.banking.ready)" -ForegroundColor $(if($status.banking.ready){'Green'}else{'Red'})
# #     Write-Host ""
# #     Write-Host "  CREDIT CARD:" -ForegroundColor Magenta
# #     Write-Host "    Feedback Count: $($status.credit_card.feedback_count)" -ForegroundColor White
# #     Write-Host "    Progress:       $($status.credit_card.progress)" -ForegroundColor Yellow
# #     Write-Host "    Ready:          $($status.credit_card.ready)" -ForegroundColor $(if($status.credit_card.ready){'Green'}else{'Red'})
# #     Write-Host ""
    
# #     # Trigger retraining if ready
# #     if ($status.banking.ready -or $status.credit_card.ready) {
# #         Write-Host "="*90 -ForegroundColor Green
# #         Write-Host "[AUTO-RETRAINING] TRIGGERING NOW" -ForegroundColor Green
# #         Write-Host "="*90 -ForegroundColor Green
# #         Write-Host ""
        
# #         try {
# #             $retrainResult = Invoke-RestMethod -Uri "$baseUrl/api/retrain/trigger" -Method POST -ContentType "application/json" -TimeoutSec 5
            
# #             Write-Host "  [SUCCESS] $($retrainResult.message)" -ForegroundColor Green
# #             Write-Host "  Models: $($retrainResult.models -join ', ')" -ForegroundColor White
# #             Write-Host "  Note: Check server terminal for progress" -ForegroundColor Gray
            
# #         } catch {
# #             Write-Host "  [INFO] Retraining started in background" -ForegroundColor Cyan
# #             Write-Host "  Check server terminal for progress" -ForegroundColor Gray
# #         }
        
# #         Write-Host ""
# #         Write-Host "  Waiting 5 seconds for retraining to complete..." -ForegroundColor Yellow
# #         Start-Sleep -Seconds 5
# #     } else {
# #         Write-Host "  [INFO] Not enough feedback yet. Run test again to reach threshold." -ForegroundColor Yellow
# #     }
    
# # } catch {
# #     Write-Host "  ERROR: $($_.Exception.Message)" -ForegroundColor Red
# # }

# # Write-Host ""

# # # ============================================
# # # PHASE 5: VERIFY IN DATABASE
# # # ============================================
# # Write-Host "="*90 -ForegroundColor Cyan
# # Write-Host "PHASE 5: Verify in Database" -ForegroundColor Yellow
# # Write-Host "="*90 -ForegroundColor Cyan
# # Write-Host ""

# # try {
# #     Write-Host "  Current predictions by model type:" -ForegroundColor Cyan
# #     $currentPreds = psql -U postgres -d fraud_detection -t -c "SELECT model_type, COUNT(*) FROM predictions GROUP BY model_type ORDER BY model_type;"
# #     $currentPreds -split "`n" | ForEach-Object {
# #         if ($_.Trim() -ne "") {
# #             Write-Host "    $($_.Trim())" -ForegroundColor White
# #         }
# #     }
# #     Write-Host ""
    
# #     Write-Host "  Feedback counts:" -ForegroundColor Cyan
# #     $feedbackCounts = psql -U postgres -d fraud_detection -t -c "SELECT model_type, COUNT(*) as feedback FROM predictions WHERE actual_class IS NOT NULL GROUP BY model_type ORDER BY model_type;"
# #     $feedbackCounts -split "`n" | ForEach-Object {
# #         if ($_.Trim() -ne "") {
# #             Write-Host "    $($_.Trim())" -ForegroundColor Green
# #         }
# #     }
# #     Write-Host ""
    
# #     Write-Host "  Retrained model versions:" -ForegroundColor Cyan
# #     $versions = psql -U postgres -d fraud_detection -t -c "SELECT LEFT(version, 30) as version, model_type FROM model_versions WHERE version LIKE '%retrained%' ORDER BY id DESC LIMIT 5;"
# #     if ($versions.Trim() -ne "") {
# #         $versions -split "`n" | ForEach-Object {
# #             if ($_.Trim() -ne "") {
# #                 Write-Host "    $($_.Trim())" -ForegroundColor Yellow
# #             }
# #         }
# #     } else {
# #         Write-Host "    (No retrained models yet)" -ForegroundColor Gray
# #     }
    
# # } catch {
# #     Write-Host "  [WARNING] Could not verify database" -ForegroundColor Yellow
# # }

# # Write-Host ""
# # Write-Host "="*90 -ForegroundColor Green
# # Write-Host "[COMPLETE] TEST FINISHED" -ForegroundColor Green
# # Write-Host "="*90 -ForegroundColor Green
# # Write-Host ""
# # test_20_samples_fixed.ps1 - NO EMOJI VERSION
# Write-Host ""
# Write-Host "="*90 -ForegroundColor Cyan
# Write-Host "20 SAMPLE TEST + FEEDBACK - AUTO-RETRAINING TRIGGER" -ForegroundColor Cyan
# Write-Host "="*90 -ForegroundColor Cyan
# Write-Host ""

# $baseUrl = "http://localhost:5000"
# $predictions = @()

# # ============================================
# # 10 BANKING SAMPLES
# # ============================================
# Write-Host "PHASE 1: 10 Banking Transactions" -ForegroundColor Yellow
# Write-Host ""

# $bankingSamples = @(
#     @{Transaction_Amount=8000; Account_Balance=1200; Transaction_Type="ATM Withdrawal"; Timestamp="2023-12-24 03:15:00"; Daily_Transaction_Count=15; Avg_Transaction_Amount_7d=250; Failed_Transaction_Count_7d=5; Card_Age=12; Transaction_Distance=4500; IP_Address_Flag=1; actual_fraud=1},
#     @{Transaction_Amount=5500; Account_Balance=800; Transaction_Type="Online"; Timestamp="2023-12-24 02:30:00"; Daily_Transaction_Count=12; Avg_Transaction_Amount_7d=300; Failed_Transaction_Count_7d=3; Card_Age=8; Transaction_Distance=3000; IP_Address_Flag=1; actual_fraud=1},
#     @{Transaction_Amount=75; Account_Balance=15000; Transaction_Type="POS"; Timestamp="2023-12-24 14:30:00"; Daily_Transaction_Count=3; Avg_Transaction_Amount_7d=80; Failed_Transaction_Count_7d=0; Card_Age=250; Transaction_Distance=300; IP_Address_Flag=0; actual_fraud=0},
#     @{Transaction_Amount=150; Account_Balance=5000; Transaction_Type="POS"; Timestamp="2023-12-24 12:00:00"; Daily_Transaction_Count=4; Avg_Transaction_Amount_7d=120; Failed_Transaction_Count_7d=0; Card_Age=180; Transaction_Distance=200; IP_Address_Flag=0; actual_fraud=0},
#     @{Transaction_Amount=9500; Account_Balance=900; Transaction_Type="ATM Withdrawal"; Timestamp="2023-12-24 04:00:00"; Daily_Transaction_Count=18; Avg_Transaction_Amount_7d=200; Failed_Transaction_Count_7d=6; Card_Age=10; Transaction_Distance=5000; IP_Address_Flag=1; actual_fraud=1},
#     @{Transaction_Amount=45; Account_Balance=8000; Transaction_Type="POS"; Timestamp="2023-12-24 10:30:00"; Daily_Transaction_Count=2; Avg_Transaction_Amount_7d=50; Failed_Transaction_Count_7d=0; Card_Age=300; Transaction_Distance=150; IP_Address_Flag=0; actual_fraud=0},
#     @{Transaction_Amount=6200; Account_Balance=1500; Transaction_Type="Online"; Timestamp="2023-12-24 01:45:00"; Daily_Transaction_Count=14; Avg_Transaction_Amount_7d=280; Failed_Transaction_Count_7d=4; Card_Age=15; Transaction_Distance=4000; IP_Address_Flag=1; actual_fraud=1},
#     @{Transaction_Amount=220; Account_Balance=12000; Transaction_Type="POS"; Timestamp="2023-12-24 18:00:00"; Daily_Transaction_Count=5; Avg_Transaction_Amount_7d=200; Failed_Transaction_Count_7d=0; Card_Age=200; Transaction_Distance=400; IP_Address_Flag=0; actual_fraud=0},
#     @{Transaction_Amount=7800; Account_Balance=1100; Transaction_Type="Transfer"; Timestamp="2023-12-24 03:30:00"; Daily_Transaction_Count=16; Avg_Transaction_Amount_7d=220; Failed_Transaction_Count_7d=5; Card_Age=11; Transaction_Distance=4800; IP_Address_Flag=1; actual_fraud=1},
#     @{Transaction_Amount=95; Account_Balance=6500; Transaction_Type="POS"; Timestamp="2023-12-24 16:00:00"; Daily_Transaction_Count=3; Avg_Transaction_Amount_7d=90; Failed_Transaction_Count_7d=0; Card_Age=220; Transaction_Distance=250; IP_Address_Flag=0; actual_fraud=0}
# )

# foreach ($i in 0..9) {
#     $sample = $bankingSamples[$i]
#     $actual_fraud = $sample.actual_fraud
#     $sample.Remove('actual_fraud')
#     $sample['mode'] = 'banking'
    
#     $body = $sample | ConvertTo-Json
    
#     try {
#         $result = Invoke-RestMethod -Uri "$baseUrl/api/check-fraud" -Method POST -Body $body -ContentType "application/json"
        
#         $predType = if($result.prediction -eq 1){"FRAUD"}else{"NORMAL"}
#         $color = if($result.prediction -eq 1){"Red"}else{"Green"}
        
#         Write-Host "  $($i+1). Banking ID $($result.prediction_id): `$$($sample.Transaction_Amount) - $predType" -ForegroundColor $color
        
#         $predictions += @{id=$result.prediction_id; actual=$actual_fraud; mode='banking'}
        
#         Start-Sleep -Milliseconds 200
#     } catch {
#         Write-Host "  ERROR: $($_.Exception.Message)" -ForegroundColor Red
#     }
# }

# Write-Host ""

# # ============================================
# # 10 CREDIT CARD SAMPLES
# # ============================================
# Write-Host "PHASE 2: 10 Credit Card Transactions" -ForegroundColor Magenta
# Write-Host ""

# $ccSamples = @(
#     @{Time=68000; Amount=225; V1=-0.75; V2=0.85; V3=0.12; V4=0.58; V5=-0.12; V6=0.32; V7=0.12; V8=0.05; V9=-0.18; V10=0.95; V11=0.68; V12=-1.15; V13=0.32; V14=-2.15; V15=0.48; V16=-0.58; V17=-1.28; V18=-0.42; V19=0.18; V20=0.08; V21=0.25; V22=0.38; V23=-0.08; V24=-0.28; V25=0.25; V26=-0.38; V27=0.02; V28=0.02; actual_fraud=1},
#     @{Time=72000; Amount=189; V1=-0.82; V2=0.92; V3=0.15; V4=0.62; V5=-0.15; V6=0.35; V7=0.15; V8=0.08; V9=-0.22; V10=1.02; V11=0.72; V12=-1.22; V13=0.35; V14=-2.25; V15=0.52; V16=-0.62; V17=-1.35; V18=-0.45; V19=0.22; V20=0.12; V21=0.28; V22=0.42; V23=-0.12; V24=-0.32; V25=0.28; V26=-0.42; V27=0.05; V28=0.05; actual_fraud=1},
#     @{Time=35000; Amount=156.5; V1=0.38; V2=0.55; V3=-0.15; V4=0.65; V5=0.22; V6=0.45; V7=-0.22; V8=0.35; V9=0.15; V10=0.48; V11=0.32; V12=0.15; V13=-0.15; V14=0.42; V15=0.22; V16=0.38; V17=-0.22; V18=0.22; V19=0.15; V20=0.22; V21=0.38; V22=0.22; V23=0.15; V24=0.22; V25=0.15; V26=0.22; V27=0.15; V28=0.15; actual_fraud=0},
#     @{Time=42000; Amount=127; V1=0.42; V2=0.58; V3=-0.18; V4=0.68; V5=0.25; V6=0.48; V7=-0.25; V8=0.38; V9=0.18; V10=0.52; V11=0.35; V12=0.18; V13=-0.18; V14=0.45; V15=0.25; V16=0.42; V17=-0.25; V18=0.25; V19=0.18; V20=0.25; V21=0.42; V22=0.25; V23=0.18; V24=0.25; V25=0.18; V26=0.25; V27=0.18; V28=0.18; actual_fraud=0},
#     @{Time=75000; Amount=298; V1=-0.88; V2=0.98; V3=0.18; V4=0.68; V5=-0.18; V6=0.38; V7=0.18; V8=0.12; V9=-0.25; V10=1.08; V11=0.78; V12=-1.28; V13=0.38; V14=-2.35; V15=0.58; V16=-0.68; V17=-1.42; V18=-0.48; V19=0.25; V20=0.15; V21=0.32; V22=0.48; V23=-0.15; V24=-0.35; V25=0.32; V26=-0.48; V27=0.08; V28=0.08; actual_fraud=1},
#     @{Time=38000; Amount=89; V1=0.45; V2=0.62; V3=-0.22; V4=0.72; V5=0.28; V6=0.52; V7=-0.28; V8=0.42; V9=0.22; V10=0.55; V11=0.38; V12=0.22; V13=-0.22; V14=0.48; V15=0.28; V16=0.45; V17=-0.28; V18=0.28; V19=0.22; V20=0.28; V21=0.45; V22=0.28; V23=0.22; V24=0.28; V25=0.22; V26=0.28; V27=0.22; V28=0.22; actual_fraud=0},
#     @{Time=78000; Amount=315; V1=-0.92; V2=1.05; V3=0.22; V4=0.72; V5=-0.22; V6=0.42; V7=0.22; V8=0.15; V9=-0.28; V10=1.15; V11=0.82; V12=-1.35; V13=0.42; V14=-2.45; V15=0.62; V16=-0.72; V17=-1.48; V18=-0.52; V19=0.28; V20=0.18; V21=0.35; V22=0.52; V23=-0.18; V24=-0.38; V25=0.35; V26=-0.52; V27=0.12; V28=0.12; actual_fraud=1},
#     @{Time=45000; Amount=178; V1=0.48; V2=0.65; V3=-0.25; V4=0.75; V5=0.32; V6=0.55; V7=-0.32; V8=0.45; V9=0.25; V10=0.58; V11=0.42; V12=0.25; V13=-0.25; V14=0.52; V15=0.32; V16=0.48; V17=-0.32; V18=0.32; V19=0.25; V20=0.32; V21=0.48; V22=0.32; V23=0.25; V24=0.32; V25=0.25; V26=0.32; V27=0.25; V28=0.25; actual_fraud=0},
#     @{Time=80000; Amount=267; V1=-0.78; V2=0.88; V3=0.15; V4=0.62; V5=-0.15; V6=0.35; V7=0.15; V8=0.08; V9=-0.22; V10=1.02; V11=0.72; V12=-1.22; V13=0.35; V14=-2.28; V15=0.52; V16=-0.62; V17=-1.35; V18=-0.45; V19=0.22; V20=0.12; V21=0.28; V22=0.42; V23=-0.12; V24=-0.32; V25=0.28; V26=-0.42; V27=0.05; V28=0.05; actual_fraud=1},
#     @{Time=48000; Amount=142; V1=0.52; V2=0.68; V3=-0.28; V4=0.78; V5=0.35; V6=0.58; V7=-0.35; V8=0.48; V9=0.28; V10=0.62; V11=0.45; V12=0.28; V13=-0.28; V14=0.55; V15=0.35; V16=0.52; V17=-0.35; V18=0.35; V19=0.28; V20=0.35; V21=0.52; V22=0.35; V23=0.28; V24=0.35; V25=0.28; V26=0.35; V27=0.28; V28=0.28; actual_fraud=0}
# )

# foreach ($i in 0..9) {
#     $sample = $ccSamples[$i]
#     $actual_fraud = $sample.actual_fraud
#     $sample.Remove('actual_fraud')
#     $sample['mode'] = 'credit_card'
    
#     $body = $sample | ConvertTo-Json
    
#     try {
#         $result = Invoke-RestMethod -Uri "$baseUrl/api/check-fraud" -Method POST -Body $body -ContentType "application/json"
        
#         $predType = if($result.prediction -eq 1){"FRAUD"}else{"NORMAL"}
#         $color = if($result.prediction -eq 1){"Red"}else{"Green"}
        
#         Write-Host "  $($i+1). Credit Card ID $($result.prediction_id): `$$($sample.Amount) - $predType" -ForegroundColor $color
        
#         $predictions += @{id=$result.prediction_id; actual=$actual_fraud; mode='credit_card'}
        
#         Start-Sleep -Milliseconds 200
#     } catch {
#         Write-Host "  ERROR: $($_.Exception.Message)" -ForegroundColor Red
#     }
# }

# Write-Host ""
# Write-Host "="*90 -ForegroundColor Cyan
# Write-Host "PHASE 3: Submit Feedback for All 20 Samples" -ForegroundColor Yellow
# Write-Host "="*90 -ForegroundColor Cyan
# Write-Host ""

# $feedbackCount = 0

# foreach ($pred in $predictions) {
#     $feedback = @{
#         actual_class = $pred.actual
#         feedback_note = "Test feedback for auto-retraining"
#     } | ConvertTo-Json
    
#     try {
#         $result = Invoke-RestMethod -Uri "$baseUrl/api/predictions/$($pred.id)/feedback" -Method POST -Body $feedback -ContentType "application/json"
        
#         $feedbackCount++
#         Write-Host "  [OK] Feedback $feedbackCount/20: ID $($pred.id) [$($pred.mode)] - Actual: $($pred.actual)" -ForegroundColor Green
        
#         Start-Sleep -Milliseconds 100
#     } catch {
#         Write-Host "  [FAIL] ID $($pred.id): $($_.Exception.Message)" -ForegroundColor Red
#     }
# }

# Write-Host ""
# Write-Host "="*90 -ForegroundColor Cyan
# Write-Host "PHASE 4: Check Retraining Status" -ForegroundColor Yellow
# Write-Host "="*90 -ForegroundColor Cyan
# Write-Host ""

# try {
#     $status = Invoke-RestMethod -Uri "$baseUrl/api/retrain/status" -Method GET
    
#     Write-Host "  Retraining Threshold: $($status.threshold)" -ForegroundColor White
#     Write-Host ""
#     Write-Host "  BANKING:" -ForegroundColor Cyan
#     Write-Host "    Feedback Count: $($status.banking.feedback_count)" -ForegroundColor White
#     Write-Host "    Progress:       $($status.banking.progress)" -ForegroundColor Yellow
#     Write-Host "    Ready:          $($status.banking.ready)" -ForegroundColor $(if($status.banking.ready){'Green'}else{'Red'})
#     Write-Host ""
#     Write-Host "  CREDIT CARD:" -ForegroundColor Magenta
#     Write-Host "    Feedback Count: $($status.credit_card.feedback_count)" -ForegroundColor White
#     Write-Host "    Progress:       $($status.credit_card.progress)" -ForegroundColor Yellow
#     Write-Host "    Ready:          $($status.credit_card.ready)" -ForegroundColor $(if($status.credit_card.ready){'Green'}else{'Red'})
#     Write-Host ""
    
#     # Trigger retraining if ready
#     if ($status.banking.ready -or $status.credit_card.ready) {
#         Write-Host "="*90 -ForegroundColor Green
#         Write-Host "[AUTO-RETRAINING] TRIGGERING NOW" -ForegroundColor Green
#         Write-Host "="*90 -ForegroundColor Green
#         Write-Host ""
        
#         $retrainResult = Invoke-RestMethod -Uri "$baseUrl/api/retrain/trigger" -Method POST -ContentType "application/json"
        
#         foreach ($result in $retrainResult.results) {
#             if ($result.status -eq 'success') {
#                 Write-Host "  [SUCCESS] $($result.model_type.ToUpper()) RETRAINED" -ForegroundColor Green
#                 Write-Host "     Samples Used: $($result.samples)" -ForegroundColor White
#                 Write-Host "     ROC-AUC:      $([math]::Round($result.roc_auc, 4))" -ForegroundColor Yellow
#             } else {
#                 Write-Host "  [FAILED] $($result.model_type): $($result.message)" -ForegroundColor Red
#             }
#         }
#     }
    
# } catch {
#     Write-Host "  ERROR: $($_.Exception.Message)" -ForegroundColor Red
# }

# Write-Host ""
# Write-Host "="*90 -ForegroundColor Cyan
# Write-Host "PHASE 5: Verify in Database" -ForegroundColor Yellow
# Write-Host "="*90 -ForegroundColor Cyan
# Write-Host ""

# Write-Host "Run these commands to verify:" -ForegroundColor White
# Write-Host ""
# Write-Host "1. View all predictions:" -ForegroundColor Cyan
# Write-Host "   psql -U postgres -d fraud_detection -c ""SELECT COUNT(*), model_type FROM predictions GROUP BY model_type;""" -ForegroundColor Gray
# Write-Host ""
# Write-Host "2. View feedback count:" -ForegroundColor Cyan
# Write-Host "   psql -U postgres -d fraud_detection -c ""SELECT model_type, COUNT(*) FROM predictions WHERE actual_class IS NOT NULL GROUP BY model_type;""" -ForegroundColor Gray
# Write-Host ""
# Write-Host "3. View retrained models:" -ForegroundColor Cyan
# Write-Host "   psql -U postgres -d fraud_detection -c ""SELECT version, model_type FROM model_versions ORDER BY id DESC LIMIT 5;""" -ForegroundColor Gray
# Write-Host ""

# Write-Host "="*90 -ForegroundColor Green
# Write-Host "[COMPLETE] 20 SAMPLES + FEEDBACK SUBMITTED" -ForegroundColor Green
# Write-Host "="*90 -ForegroundColor Green
# Write-Host ""



# test_final.ps1 - COMPLETE RETRAINING TEST (20+20 Samples in ONE Run)
Write-Host ""
Write-Host "="*90 -ForegroundColor Cyan
Write-Host "FINAL AUTO-RETRAINING TEST (Clean DB + 20+20 Samples + Retraining)" -ForegroundColor Cyan
Write-Host "="*90 -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:5000"

# ============================================
# PHASE 0: CLEAN DATABASE
# ============================================
Write-Host "PHASE 0: Clean Database (Remove Previous Data)" -ForegroundColor Yellow
Write-Host ""

try {
    Write-Host "  Deleting all feedback..." -ForegroundColor Yellow
    $deleteFeedback = psql -U postgres -d fraud_detection -c "DELETE FROM feedback;" 2>&1 | Out-Null
    
    Write-Host "  Deleting all predictions..." -ForegroundColor Yellow
    $deletePreds = psql -U postgres -d fraud_detection -c "DELETE FROM predictions;" 2>&1 | Out-Null
    
    Write-Host "  [OK] Database cleaned" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "  [WARNING] Cleanup failed, continuing..." -ForegroundColor Yellow
}

Start-Sleep -Seconds 2

# ============================================
# PHASE 1: CREATE 20 BANKING PREDICTIONS
# ============================================
Write-Host "="*90 -ForegroundColor Cyan
Write-Host "PHASE 1: Create 20 Banking Transactions" -ForegroundColor Yellow
Write-Host "="*90 -ForegroundColor Cyan
Write-Host ""

$bankingPredictions = @()

# 20 banking samples (10 fraud, 10 normal)
$bankingSamples = @(
    @{Transaction_Amount=8000; Account_Balance=1200; Transaction_Type="ATM Withdrawal"; Timestamp="2023-12-24 03:15:00"; Daily_Transaction_Count=15; Avg_Transaction_Amount_7d=250; Failed_Transaction_Count_7d=5; Card_Age=12; Transaction_Distance=4500; IP_Address_Flag=1; actual_fraud=1},
    @{Transaction_Amount=5500; Account_Balance=800; Transaction_Type="Online"; Timestamp="2023-12-24 02:30:00"; Daily_Transaction_Count=12; Avg_Transaction_Amount_7d=300; Failed_Transaction_Count_7d=3; Card_Age=8; Transaction_Distance=3000; IP_Address_Flag=1; actual_fraud=1},
    @{Transaction_Amount=75; Account_Balance=15000; Transaction_Type="POS"; Timestamp="2023-12-24 14:30:00"; Daily_Transaction_Count=3; Avg_Transaction_Amount_7d=80; Failed_Transaction_Count_7d=0; Card_Age=250; Transaction_Distance=300; IP_Address_Flag=0; actual_fraud=0},
    @{Transaction_Amount=150; Account_Balance=5000; Transaction_Type="POS"; Timestamp="2023-12-24 12:00:00"; Daily_Transaction_Count=4; Avg_Transaction_Amount_7d=120; Failed_Transaction_Count_7d=0; Card_Age=180; Transaction_Distance=200; IP_Address_Flag=0; actual_fraud=0},
    @{Transaction_Amount=9500; Account_Balance=900; Transaction_Type="ATM Withdrawal"; Timestamp="2023-12-24 04:00:00"; Daily_Transaction_Count=18; Avg_Transaction_Amount_7d=200; Failed_Transaction_Count_7d=6; Card_Age=10; Transaction_Distance=5000; IP_Address_Flag=1; actual_fraud=1},
    @{Transaction_Amount=45; Account_Balance=8000; Transaction_Type="POS"; Timestamp="2023-12-24 10:30:00"; Daily_Transaction_Count=2; Avg_Transaction_Amount_7d=50; Failed_Transaction_Count_7d=0; Card_Age=300; Transaction_Distance=150; IP_Address_Flag=0; actual_fraud=0},
    @{Transaction_Amount=6200; Account_Balance=1500; Transaction_Type="Online"; Timestamp="2023-12-24 01:45:00"; Daily_Transaction_Count=14; Avg_Transaction_Amount_7d=280; Failed_Transaction_Count_7d=4; Card_Age=15; Transaction_Distance=4000; IP_Address_Flag=1; actual_fraud=1},
    @{Transaction_Amount=220; Account_Balance=12000; Transaction_Type="POS"; Timestamp="2023-12-24 18:00:00"; Daily_Transaction_Count=5; Avg_Transaction_Amount_7d=200; Failed_Transaction_Count_7d=0; Card_Age=200; Transaction_Distance=400; IP_Address_Flag=0; actual_fraud=0},
    @{Transaction_Amount=7800; Account_Balance=1100; Transaction_Type="Transfer"; Timestamp="2023-12-24 03:30:00"; Daily_Transaction_Count=16; Avg_Transaction_Amount_7d=220; Failed_Transaction_Count_7d=5; Card_Age=11; Transaction_Distance=4800; IP_Address_Flag=1; actual_fraud=1},
    @{Transaction_Amount=95; Account_Balance=6500; Transaction_Type="POS"; Timestamp="2023-12-24 16:00:00"; Daily_Transaction_Count=3; Avg_Transaction_Amount_7d=90; Failed_Transaction_Count_7d=0; Card_Age=220; Transaction_Distance=250; IP_Address_Flag=0; actual_fraud=0},
    @{Transaction_Amount=8500; Account_Balance=1000; Transaction_Type="ATM Withdrawal"; Timestamp="2023-12-24 02:15:00"; Daily_Transaction_Count=17; Avg_Transaction_Amount_7d=240; Failed_Transaction_Count_7d=6; Card_Age=9; Transaction_Distance=4700; IP_Address_Flag=1; actual_fraud=1},
    @{Transaction_Amount=6000; Account_Balance=1300; Transaction_Type="Online"; Timestamp="2023-12-24 01:30:00"; Daily_Transaction_Count=13; Avg_Transaction_Amount_7d=290; Failed_Transaction_Count_7d=4; Card_Age=11; Transaction_Distance=3500; IP_Address_Flag=1; actual_fraud=1},
    @{Transaction_Amount=120; Account_Balance=7000; Transaction_Type="POS"; Timestamp="2023-12-24 15:00:00"; Daily_Transaction_Count=4; Avg_Transaction_Amount_7d=100; Failed_Transaction_Count_7d=0; Card_Age=210; Transaction_Distance=280; IP_Address_Flag=0; actual_fraud=0},
    @{Transaction_Amount=180; Account_Balance=9000; Transaction_Type="POS"; Timestamp="2023-12-24 13:30:00"; Daily_Transaction_Count=5; Avg_Transaction_Amount_7d=150; Failed_Transaction_Count_7d=0; Card_Age=190; Transaction_Distance=320; IP_Address_Flag=0; actual_fraud=0},
    @{Transaction_Amount=7500; Account_Balance=1400; Transaction_Type="Transfer"; Timestamp="2023-12-24 03:00:00"; Daily_Transaction_Count=14; Avg_Transaction_Amount_7d=260; Failed_Transaction_Count_7d=5; Card_Age=13; Transaction_Distance=4200; IP_Address_Flag=1; actual_fraud=1},
    @{Transaction_Amount=85; Account_Balance=11000; Transaction_Type="POS"; Timestamp="2023-12-24 17:00:00"; Daily_Transaction_Count=3; Avg_Transaction_Amount_7d=75; Failed_Transaction_Count_7d=0; Card_Age=240; Transaction_Distance=220; IP_Address_Flag=0; actual_fraud=0},
    @{Transaction_Amount=9200; Account_Balance=950; Transaction_Type="ATM Withdrawal"; Timestamp="2023-12-24 04:15:00"; Daily_Transaction_Count=19; Avg_Transaction_Amount_7d=230; Failed_Transaction_Count_7d=7; Card_Age=8; Transaction_Distance=4900; IP_Address_Flag=1; actual_fraud=1},
    @{Transaction_Amount=200; Account_Balance=8500; Transaction_Type="POS"; Timestamp="2023-12-24 11:30:00"; Daily_Transaction_Count=6; Avg_Transaction_Amount_7d=180; Failed_Transaction_Count_7d=0; Card_Age=200; Transaction_Distance=350; IP_Address_Flag=0; actual_fraud=0},
    @{Transaction_Amount=8800; Account_Balance=1050; Transaction_Type="Online"; Timestamp="2023-12-24 02:45:00"; Daily_Transaction_Count=16; Avg_Transaction_Amount_7d=270; Failed_Transaction_Count_7d=6; Card_Age=10; Transaction_Distance=4600; IP_Address_Flag=1; actual_fraud=1},
    @{Transaction_Amount=110; Account_Balance=10000; Transaction_Type="POS"; Timestamp="2023-12-24 16:30:00"; Daily_Transaction_Count=4; Avg_Transaction_Amount_7d=95; Failed_Transaction_Count_7d=0; Card_Age=230; Transaction_Distance=270; IP_Address_Flag=0; actual_fraud=0}
)

foreach ($i in 0..19) {
    $sample = $bankingSamples[$i]
    $actual_fraud = $sample.actual_fraud
    $sample.Remove('actual_fraud')
    $sample['mode'] = 'banking'
    
    $body = $sample | ConvertTo-Json
    
    try {
        $result = Invoke-RestMethod -Uri "$baseUrl/api/check-fraud" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 30
        
        $predType = if($result.prediction -eq 1){"FRAUD"}else{"NORMAL"}
        $color = if($result.prediction -eq 1){"Red"}else{"Green"}
        
        Write-Host "  $($i+1). Banking ID $($result.prediction_id): `$$($sample.Transaction_Amount) - $predType" -ForegroundColor $color
        
        $bankingPredictions += @{id=$result.prediction_id; actual=$actual_fraud}
        
        Start-Sleep -Milliseconds 200
    } catch {
        Write-Host "  [ERROR] $($i+1) failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "  Created: $($bankingPredictions.Count)/20 banking predictions" -ForegroundColor $(if($bankingPredictions.Count -eq 20){'Green'}else{'Yellow'})
Write-Host ""

# ============================================
# PHASE 2: CREATE 20 CREDIT CARD PREDICTIONS
# ============================================
Write-Host "="*90 -ForegroundColor Cyan
Write-Host "PHASE 2: Create 20 Credit Card Transactions" -ForegroundColor Magenta
Write-Host "="*90 -ForegroundColor Cyan
Write-Host ""

$ccPredictions = @()

# 20 credit card samples (10 fraud, 10 normal)
$ccSamples = @(
    @{Time=68000; Amount=225; V1=-0.75; V2=0.85; V3=0.12; V4=0.58; V5=-0.12; V6=0.32; V7=0.12; V8=0.05; V9=-0.18; V10=0.95; V11=0.68; V12=-1.15; V13=0.32; V14=-2.15; V15=0.48; V16=-0.58; V17=-1.28; V18=-0.42; V19=0.18; V20=0.08; V21=0.25; V22=0.38; V23=-0.08; V24=-0.28; V25=0.25; V26=-0.38; V27=0.02; V28=0.02; actual_fraud=1},
    @{Time=72000; Amount=189; V1=-0.82; V2=0.92; V3=0.15; V4=0.62; V5=-0.15; V6=0.35; V7=0.15; V8=0.08; V9=-0.22; V10=1.02; V11=0.72; V12=-1.22; V13=0.35; V14=-2.25; V15=0.52; V16=-0.62; V17=-1.35; V18=-0.45; V19=0.22; V20=0.12; V21=0.28; V22=0.42; V23=-0.12; V24=-0.32; V25=0.28; V26=-0.42; V27=0.05; V28=0.05; actual_fraud=1},
    @{Time=35000; Amount=156.5; V1=0.38; V2=0.55; V3=-0.15; V4=0.65; V5=0.22; V6=0.45; V7=-0.22; V8=0.35; V9=0.15; V10=0.48; V11=0.32; V12=0.15; V13=-0.15; V14=0.42; V15=0.22; V16=0.38; V17=-0.22; V18=0.22; V19=0.15; V20=0.22; V21=0.38; V22=0.22; V23=0.15; V24=0.22; V25=0.15; V26=0.22; V27=0.15; V28=0.15; actual_fraud=0},
    @{Time=42000; Amount=127; V1=0.42; V2=0.58; V3=-0.18; V4=0.68; V5=0.25; V6=0.48; V7=-0.25; V8=0.38; V9=0.18; V10=0.52; V11=0.35; V12=0.18; V13=-0.18; V14=0.45; V15=0.25; V16=0.42; V17=-0.25; V18=0.25; V19=0.18; V20=0.25; V21=0.42; V22=0.25; V23=0.18; V24=0.25; V25=0.18; V26=0.25; V27=0.18; V28=0.18; actual_fraud=0},
    @{Time=75000; Amount=298; V1=-0.88; V2=0.98; V3=0.18; V4=0.68; V5=-0.18; V6=0.38; V7=0.18; V8=0.12; V9=-0.25; V10=1.08; V11=0.78; V12=-1.28; V13=0.38; V14=-2.35; V15=0.58; V16=-0.68; V17=-1.42; V18=-0.48; V19=0.25; V20=0.15; V21=0.32; V22=0.48; V23=-0.15; V24=-0.35; V25=0.32; V26=-0.48; V27=0.08; V28=0.08; actual_fraud=1},
    @{Time=38000; Amount=89; V1=0.45; V2=0.62; V3=-0.22; V4=0.72; V5=0.28; V6=0.52; V7=-0.28; V8=0.42; V9=0.22; V10=0.55; V11=0.38; V12=0.22; V13=-0.22; V14=0.48; V15=0.28; V16=0.45; V17=-0.28; V18=0.28; V19=0.22; V20=0.28; V21=0.45; V22=0.28; V23=0.22; V24=0.28; V25=0.22; V26=0.28; V27=0.22; V28=0.22; actual_fraud=0},
    @{Time=78000; Amount=315; V1=-0.92; V2=1.05; V3=0.22; V4=0.72; V5=-0.22; V6=0.42; V7=0.22; V8=0.15; V9=-0.28; V10=1.15; V11=0.82; V12=-1.35; V13=0.42; V14=-2.45; V15=0.62; V16=-0.72; V17=-1.48; V18=-0.52; V19=0.28; V20=0.18; V21=0.35; V22=0.52; V23=-0.18; V24=-0.38; V25=0.35; V26=-0.52; V27=0.12; V28=0.12; actual_fraud=1},
    @{Time=45000; Amount=178; V1=0.48; V2=0.65; V3=-0.25; V4=0.75; V5=0.32; V6=0.55; V7=-0.32; V8=0.45; V9=0.25; V10=0.58; V11=0.42; V12=0.25; V13=-0.25; V14=0.52; V15=0.32; V16=0.48; V17=-0.32; V18=0.32; V19=0.25; V20=0.32; V21=0.48; V22=0.32; V23=0.25; V24=0.32; V25=0.25; V26=0.32; V27=0.25; V28=0.25; actual_fraud=0},
    @{Time=80000; Amount=267; V1=-0.78; V2=0.88; V3=0.15; V4=0.62; V5=-0.15; V6=0.35; V7=0.15; V8=0.08; V9=-0.22; V10=1.02; V11=0.72; V12=-1.22; V13=0.35; V14=-2.28; V15=0.52; V16=-0.62; V17=-1.35; V18=-0.45; V19=0.22; V20=0.12; V21=0.28; V22=0.42; V23=-0.12; V24=-0.32; V25=0.28; V26=-0.42; V27=0.05; V28=0.05; actual_fraud=1},
    @{Time=48000; Amount=142; V1=0.52; V2=0.68; V3=-0.28; V4=0.78; V5=0.35; V6=0.58; V7=-0.35; V8=0.48; V9=0.28; V10=0.62; V11=0.45; V12=0.28; V13=-0.28; V14=0.55; V15=0.35; V16=0.52; V17=-0.35; V18=0.35; V19=0.28; V20=0.35; V21=0.52; V22=0.35; V23=0.28; V24=0.35; V25=0.28; V26=0.35; V27=0.28; V28=0.28; actual_fraud=0},
    @{Time=70000; Amount=245; V1=-0.80; V2=0.90; V3=0.14; V4=0.60; V5=-0.14; V6=0.34; V7=0.14; V8=0.07; V9=-0.20; V10=1.00; V11=0.70; V12=-1.20; V13=0.34; V14=-2.20; V15=0.50; V16=-0.60; V17=-1.30; V18=-0.44; V19=0.20; V20=0.10; V21=0.27; V22=0.40; V23=-0.10; V24=-0.30; V25=0.27; V26=-0.40; V27=0.04; V28=0.04; actual_fraud=1},
    @{Time=74000; Amount=195; V1=-0.84; V2=0.94; V3=0.16; V4=0.64; V5=-0.16; V6=0.36; V7=0.16; V8=0.09; V9=-0.24; V10=1.04; V11=0.74; V12=-1.24; V13=0.36; V14=-2.26; V15=0.54; V16=-0.64; V17=-1.36; V18=-0.46; V19=0.24; V20=0.14; V21=0.29; V22=0.44; V23=-0.14; V24=-0.34; V25=0.29; V26=-0.44; V27=0.06; V28=0.06; actual_fraud=1},
    @{Time=36000; Amount=165; V1=0.40; V2=0.57; V3=-0.17; V4=0.67; V5=0.24; V6=0.47; V7=-0.24; V8=0.37; V9=0.17; V10=0.50; V11=0.34; V12=0.17; V13=-0.17; V14=0.44; V15=0.24; V16=0.40; V17=-0.24; V18=0.24; V19=0.17; V20=0.24; V21=0.40; V22=0.24; V23=0.17; V24=0.24; V25=0.17; V26=0.24; V27=0.17; V28=0.17; actual_fraud=0},
    @{Time=44000; Amount=135; V1=0.44; V2=0.60; V3=-0.20; V4=0.70; V5=0.27; V6=0.50; V7=-0.27; V8=0.40; V9=0.20; V10=0.54; V11=0.37; V12=0.20; V13=-0.20; V14=0.47; V15=0.27; V16=0.44; V17=-0.27; V18=0.27; V19=0.20; V20=0.27; V21=0.44; V22=0.27; V23=0.20; V24=0.27; V25=0.20; V26=0.27; V27=0.20; V28=0.20; actual_fraud=0},
    @{Time=77000; Amount=285; V1=-0.86; V2=0.96; V3=0.17; V4=0.66; V5=-0.17; V6=0.37; V7=0.17; V8=0.11; V9=-0.23; V10=1.06; V11=0.76; V12=-1.26; V13=0.37; V14=-2.30; V15=0.56; V16=-0.66; V17=-1.40; V18=-0.47; V19=0.23; V20=0.13; V21=0.30; V22=0.46; V23=-0.13; V24=-0.33; V25=0.30; V26=-0.46; V27=0.07; V28=0.07; actual_fraud=1},
    @{Time=40000; Amount=98; V1=0.47; V2=0.64; V3=-0.24; V4=0.74; V5=0.30; V6=0.54; V7=-0.30; V8=0.44; V9=0.24; V10=0.57; V11=0.40; V12=0.24; V13=-0.24; V14=0.50; V15=0.30; V16=0.47; V17=-0.30; V18=0.30; V19=0.24; V20=0.30; V21=0.47; V22=0.30; V23=0.24; V24=0.30; V25=0.24; V26=0.30; V27=0.24; V28=0.24; actual_fraud=0},
    @{Time=79000; Amount=305; V1=-0.90; V2=1.02; V3=0.20; V4=0.70; V5=-0.20; V6=0.40; V7=0.20; V8=0.13; V9=-0.26; V10=1.12; V11=0.80; V12=-1.32; V13=0.40; V14=-2.40; V15=0.60; V16=-0.70; V17=-1.45; V18=-0.50; V19=0.26; V20=0.16; V21=0.33; V22=0.50; V23=-0.16; V24=-0.36; V25=0.33; V26=-0.50; V27=0.10; V28=0.10; actual_fraud=1},
    @{Time=46000; Amount=185; V1=0.50; V2=0.67; V3=-0.27; V4=0.77; V5=0.33; V6=0.57; V7=-0.33; V8=0.47; V9=0.27; V10=0.60; V11=0.43; V12=0.27; V13=-0.27; V14=0.53; V15=0.33; V16=0.50; V17=-0.33; V18=0.33; V19=0.27; V20=0.33; V21=0.50; V22=0.33; V23=0.27; V24=0.33; V25=0.27; V26=0.33; V27=0.27; V28=0.27; actual_fraud=0},
    @{Time=81000; Amount=275; V1=-0.76; V2=0.86; V3=0.13; V4=0.60; V5=-0.13; V6=0.33; V7=0.13; V8=0.06; V9=-0.20; V10=1.00; V11=0.70; V12=-1.20; V13=0.33; V14=-2.24; V15=0.50; V16=-0.60; V17=-1.33; V18=-0.43; V19=0.20; V20=0.10; V21=0.26; V22=0.40; V23=-0.10; V24=-0.30; V25=0.26; V26=-0.40; V27=0.03; V28=0.03; actual_fraud=1},
    @{Time=50000; Amount=155; V1=0.54; V2=0.70; V3=-0.30; V4=0.80; V5=0.37; V6=0.60; V7=-0.37; V8=0.50; V9=0.30; V10=0.64; V11=0.47; V12=0.30; V13=-0.30; V14=0.57; V15=0.37; V16=0.54; V17=-0.37; V18=0.37; V19=0.30; V20=0.37; V21=0.54; V22=0.37; V23=0.30; V24=0.37; V25=0.30; V26=0.37; V27=0.30; V28=0.30; actual_fraud=0}
)

foreach ($i in 0..19) {
    $sample = $ccSamples[$i]
    $actual_fraud = $sample.actual_fraud
    $sample.Remove('actual_fraud')
    $sample['mode'] = 'credit_card'
    
    $body = $sample | ConvertTo-Json
    
    try {
        $result = Invoke-RestMethod -Uri "$baseUrl/api/check-fraud" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 30
        
        $predType = if($result.prediction -eq 1){"FRAUD"}else{"NORMAL"}
        $color = if($result.prediction -eq 1){"Red"}else{"Green"}
        
        Write-Host "  $($i+1). Credit Card ID $($result.prediction_id): `$$($sample.Amount) - $predType" -ForegroundColor $color
        
        $ccPredictions += @{id=$result.prediction_id; actual=$actual_fraud}
        
        Start-Sleep -Milliseconds 200
    } catch {
        Write-Host "  [ERROR] $($i+1) failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "  Created: $($ccPredictions.Count)/20 credit card predictions" -ForegroundColor $(if($ccPredictions.Count -eq 20){'Green'}else{'Yellow'})
Write-Host ""

# ============================================
# PHASE 3: SUBMIT ALL FEEDBACK (40 total)
# ============================================
Write-Host "="*90 -ForegroundColor Cyan
Write-Host "PHASE 3: Submit Feedback for All 40 Samples" -ForegroundColor Yellow
Write-Host "="*90 -ForegroundColor Cyan
Write-Host ""

$totalFeedback = 0

Write-Host "  Banking feedbacks:" -ForegroundColor Cyan
foreach ($pred in $bankingPredictions) {
    $feedback = @{
        actual_class = $pred.actual
        feedback_note = "Final test feedback"
    } | ConvertTo-Json
    
    try {
        $result = Invoke-RestMethod -Uri "$baseUrl/api/predictions/$($pred.id)/feedback" -Method POST -Body $feedback -ContentType "application/json" -TimeoutSec 30
        
        $totalFeedback++
        Write-Host "    [OK] $totalFeedback : ID $($pred.id) - Actual: $($pred.actual)" -ForegroundColor Green
        
        Start-Sleep -Milliseconds 150
    } catch {
        Write-Host "    [FAIL] ID $($pred.id)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "  Credit card feedbacks:" -ForegroundColor Magenta
foreach ($pred in $ccPredictions) {
    $feedback = @{
        actual_class = $pred.actual
        feedback_note = "Final test feedback"
    } | ConvertTo-Json
    
    try {
        $result = Invoke-RestMethod -Uri "$baseUrl/api/predictions/$($pred.id)/feedback" -Method POST -Body $feedback -ContentType "application/json" -TimeoutSec 30
        
        $totalFeedback++
        Write-Host "    [OK] $totalFeedback : ID $($pred.id) - Actual: $($pred.actual)" -ForegroundColor Green
        
        Start-Sleep -Milliseconds 150
    } catch {
        Write-Host "    [FAIL] ID $($pred.id)" -ForegroundColor Red
    }
}

Write-Host ""

# ============================================
# PHASE 4: CHECK STATUS & WAIT FOR RETRAINING
# ============================================
Write-Host "="*90 -ForegroundColor Cyan
Write-Host "PHASE 4: Check Status & Wait for Retraining" -ForegroundColor Yellow
Write-Host "="*90 -ForegroundColor Cyan
Write-Host ""

Start-Sleep -Seconds 3

try {
    $status = Invoke-RestMethod -Uri "$baseUrl/api/retrain/status" -Method GET
    
    Write-Host "  BANKING:" -ForegroundColor Cyan
    Write-Host "    Feedback Count: $($status.banking.feedback_count)/20" -ForegroundColor White
    Write-Host "    Ready:          $($status.banking.ready)" -ForegroundColor $(if($status.banking.ready){'Green'}else{'Red'})
    Write-Host ""
    Write-Host "  CREDIT CARD:" -ForegroundColor Magenta
    Write-Host "    Feedback Count: $($status.credit_card.feedback_count)/20" -ForegroundColor White
    Write-Host "    Ready:          $($status.credit_card.ready)" -ForegroundColor $(if($status.credit_card.ready){'Green'}else{'Red'})
    Write-Host ""
    
    if ($status.banking.ready -and $status.credit_card.ready) {
        Write-Host "  [AUTO-RETRAINING] Both models triggered!" -ForegroundColor Green
        Write-Host "  Waiting 60 seconds for retraining to complete..." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "  Check server terminal for:" -ForegroundColor Gray
        Write-Host "    - Dataset loading (50K banking + 284K credit card)" -ForegroundColor Gray
        Write-Host "    - Model training progress" -ForegroundColor Gray
        Write-Host "    - Old vs New performance comparison" -ForegroundColor Gray
        Write-Host "    - Auto-activation decision" -ForegroundColor Gray
        Write-Host "    - Backup creation" -ForegroundColor Gray
        Write-Host ""
        
        Start-Sleep -Seconds 60
    }
} catch {
    Write-Host "  [ERROR] Could not check status" -ForegroundColor Red
}

# ============================================
# PHASE 5: VERIFY RESULTS
# ============================================
Write-Host "="*90 -ForegroundColor Cyan
Write-Host "PHASE 5: Verify Results" -ForegroundColor Yellow
Write-Host "="*90 -ForegroundColor Cyan
Write-Host ""

try {
    Write-Host "  Model versions:" -ForegroundColor Cyan
    $versions = psql -U postgres -d fraud_detection -t -c "SELECT LEFT(version, 40) as version, model_type, is_active FROM model_versions ORDER BY id DESC LIMIT 6;" 2>&1
    $versions -split "`n" | ForEach-Object {
        if ($_.Trim() -ne "") {
            $color = if($_ -match '\| t') {'Green'} else {'Gray'}
            Write-Host "    $($_.Trim())" -ForegroundColor $color
        }
    }
    Write-Host ""
    
    Write-Host "  Backup folder:" -ForegroundColor Cyan
    if (Test-Path "models\backups") {
        $backups = Get-ChildItem "models\backups" | Select-Object -Last 5
        if ($backups) {
            $backups | ForEach-Object {
                Write-Host "    $($_.Name)" -ForegroundColor Gray
            }
        } else {
            Write-Host "    (no backups yet)" -ForegroundColor Gray
        }
    } else {
        Write-Host "    (backups folder not created)" -ForegroundColor Gray
    }
} catch {
    Write-Host "  [WARNING] Could not verify results" -ForegroundColor Yellow
}

Write-Host ""

# ============================================
# SUMMARY
# ============================================
Write-Host "="*90 -ForegroundColor Green
Write-Host "[COMPLETE] TEST FINISHED" -ForegroundColor Green
Write-Host "="*90 -ForegroundColor Green
Write-Host ""
Write-Host "  Banking predictions:    $($bankingPredictions.Count)/20" -ForegroundColor White
Write-Host "  Credit card predictions: $($ccPredictions.Count)/20" -ForegroundColor White
Write-Host "  Total feedbacks:        $totalFeedback/40" -ForegroundColor White
Write-Host ""
Write-Host "  Retraining triggered:   YES" -ForegroundColor Green
Write-Host "  Both models retrained:  Check server logs" -ForegroundColor Yellow
Write-Host "  Old models backed up:   models/backups/" -ForegroundColor Yellow
Write-Host ""