# ============================================================
# Install All Dependencies — Run Once
# ============================================================
Write-Host "Installing Python dependencies..." -ForegroundColor Cyan
pip install flask flask-cors sqlalchemy loguru xgboost scikit-learn joblib reportlab numpy pandas

Write-Host ""
Write-Host "Installing Node.js dependencies..." -ForegroundColor Cyan
Set-Location client
npm install
Set-Location ..

Write-Host ""
Write-Host "Installing Electron dependencies..." -ForegroundColor Cyan
npm install

Write-Host ""
Write-Host "All dependencies installed!" -ForegroundColor Green
Write-Host "Next step: run scripts\train_models.bat to generate ML models." -ForegroundColor Yellow
