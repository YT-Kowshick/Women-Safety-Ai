# Women Safety AI - Setup Script (Windows)
# This script sets up both backend and frontend

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Women Safety AI - Project Setup" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Backend Setup
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Step 1: Setting up Backend" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

Set-Location backend

Write-Host "Installing Python dependencies..." -ForegroundColor Blue
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Backend dependencies installed" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to install backend dependencies" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Testing backend imports..." -ForegroundColor Blue
python -c "import fastapi, uvicorn, pandas, joblib; print('All imports successful')"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Backend setup complete" -ForegroundColor Green
} else {
    Write-Host "❌ Backend import test failed" -ForegroundColor Red
    exit 1
}

Set-Location ..

# Step 2: Frontend Setup
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Step 2: Setting up Frontend" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

Set-Location frontend

Write-Host "Installing Node.js dependencies..." -ForegroundColor Blue
npm install

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Frontend dependencies installed" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to install frontend dependencies" -ForegroundColor Red
    exit 1
}

# Check if .env exists
if (-not (Test-Path .env)) {
    Write-Host "Creating .env file..." -ForegroundColor Blue
    "VITE_API_URL=http://localhost:8000" | Out-File -FilePath .env -Encoding utf8
    Write-Host "✅ .env file created" -ForegroundColor Green
} else {
    Write-Host "✅ .env file already exists" -ForegroundColor Green
}

Set-Location ..

# Summary
Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "Setup Complete! 🎉" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "To start the application:" -ForegroundColor Yellow
Write-Host ""
Write-Host "Terminal 1 - Backend:" -ForegroundColor Cyan
Write-Host "  cd backend" -ForegroundColor White
Write-Host "  uvicorn app:app --reload" -ForegroundColor White
Write-Host ""
Write-Host "Terminal 2 - Frontend:" -ForegroundColor Cyan
Write-Host "  cd frontend" -ForegroundColor White
Write-Host "  npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "Then visit:" -ForegroundColor Yellow
Write-Host "  Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "  Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "================================================" -ForegroundColor Green
