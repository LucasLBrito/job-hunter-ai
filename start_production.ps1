# Start Job Hunter AI in Production Mode (Local)

Write-Host "🚀 Starting Job Hunter AI - Production Mode" -ForegroundColor Green

# 1. Backend
Write-Host "backend..." -ForegroundColor Yellow
$backendPath = ".\apps\backend"
Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; py -m uvicorn app.main:app --host 0.0.0.0 --port 8000" -PassThru
Write-Host "✅ Backend started (Port 8000)" -ForegroundColor Green

# 2. Frontend Build & Start
Write-Host "frontend..." -ForegroundColor Yellow
$frontendPath = ".\apps\frontend"
Push-Location $frontendPath

# Check if .next exists (Build check)
# We force build to ensure production readiness
Write-Host "📦 Building frontend..." -ForegroundColor Cyan
npm run build

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Frontend Build Failed!" -ForegroundColor Red
    Pop-Location
    exit 1
}

Write-Host "✅ Frontend Build Complete. Starting..." -ForegroundColor Green
Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "cd '$frontendPath'; npm run start" -PassThru

Pop-Location

Write-Host "🎉 Production Environment Running!" -ForegroundColor Green
Write-Host "Backend: http://localhost:8000/docs"
Write-Host "Frontend: http://localhost:3000"
