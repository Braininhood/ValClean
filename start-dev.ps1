# VALClean Booking System - Start Development Servers
# This script starts both backend (Django) and frontend (Next.js) servers simultaneously

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  VALClean Booking System" -ForegroundColor Green
Write-Host "  Starting Development Servers" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get the script directory (project root)
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendPath = Join-Path $scriptPath "backend"
$frontendPath = Join-Path $scriptPath "frontend"

# Check if directories exist
if (-not (Test-Path $backendPath)) {
    Write-Host "Error: Backend directory not found at $backendPath" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $frontendPath)) {
    Write-Host "Error: Frontend directory not found at $frontendPath" -ForegroundColor Red
    exit 1
}

# Check if virtual environment exists
$venvPath = Join-Path $backendPath "venv"
if (-not (Test-Path $venvPath)) {
    Write-Host "Error: Virtual environment not found at $venvPath" -ForegroundColor Red
    Write-Host "Please create it first: cd backend; python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Check if node_modules exists
$nodeModulesPath = Join-Path $frontendPath "node_modules"
if (-not (Test-Path $nodeModulesPath)) {
    Write-Host "Warning: Frontend node_modules not found. Installing dependencies..." -ForegroundColor Yellow
    Push-Location $frontendPath
    npm install
    Pop-Location
}

# Stop any existing servers on ports 8000 and 3000
Write-Host "Checking for existing servers..." -ForegroundColor Yellow
$backendPort = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
$frontendPort = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique

if ($backendPort) {
    Write-Host "Stopping existing backend server on port 8000..." -ForegroundColor Yellow
    Stop-Process -Id $backendPort -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
}

if ($frontendPort) {
    Write-Host "Stopping existing frontend server on port 3000..." -ForegroundColor Yellow
    Stop-Process -Id $frontendPort -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
}

Write-Host ""
Write-Host "Starting Backend Server (Django)..." -ForegroundColor Cyan
Write-Host "URL: http://localhost:8000" -ForegroundColor White
Write-Host "API: http://localhost:8000/api/" -ForegroundColor White
Write-Host "Docs: http://localhost:8000/api/docs/" -ForegroundColor White
Write-Host "Admin: http://localhost:8000/admin/" -ForegroundColor White
Write-Host ""

# Start Backend Server in new window
$backendScript = @"
cd `"$backendPath`"
.\venv\Scripts\Activate.ps1
Write-Host '=== Backend Server (Django) ===' -ForegroundColor Cyan
Write-Host 'Running at: http://localhost:8000' -ForegroundColor Green
Write-Host 'Press Ctrl+C to stop' -ForegroundColor Yellow
Write-Host ''
python manage.py runserver
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendScript

# Wait 3 seconds for backend to start
Write-Host "Waiting for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "Starting Frontend Server (Next.js)..." -ForegroundColor Cyan
Write-Host "URL: http://localhost:3000" -ForegroundColor White
Write-Host ""

# Start Frontend Server in new window
$frontendScript = @"
cd `"$frontendPath`"
Write-Host '=== Frontend Server (Next.js) ===' -ForegroundColor Green
Write-Host 'Running at: http://localhost:3000' -ForegroundColor Green
Write-Host 'Press Ctrl+C to stop' -ForegroundColor Yellow
Write-Host ''
npm run dev
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendScript

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Servers Starting..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend:  http://localhost:8000" -ForegroundColor Green
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Green
Write-Host ""
Write-Host "Two PowerShell windows will open:" -ForegroundColor Yellow
Write-Host "  1. Backend server (Django)" -ForegroundColor White
Write-Host "  2. Frontend server (Next.js)" -ForegroundColor White
Write-Host ""
Write-Host "To stop servers: Press Ctrl+C in each window, or close the windows" -ForegroundColor Yellow
Write-Host ""
Write-Host "[OK] Servers are starting in separate windows..." -ForegroundColor Green
Write-Host ""
