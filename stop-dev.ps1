# VALClean Booking System - Stop Development Servers
# This script stops both backend (Django) and frontend (Next.js) servers

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  VALClean Booking System" -ForegroundColor Green
Write-Host "  Stopping Development Servers" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$stopped = $false

# Stop Backend Server (port 8000)
Write-Host "Checking Backend Server (port 8000)..." -ForegroundColor Yellow
$backendPort = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique

if ($backendPort) {
    try {
        Stop-Process -Id $backendPort -Force -ErrorAction Stop
        Write-Host "[OK] Backend server stopped (port 8000)" -ForegroundColor Green
        $stopped = $true
    } catch {
        Write-Host "[WARNING] Could not stop backend server: $_" -ForegroundColor Yellow
    }
} else {
    Write-Host "[INFO] Backend server not running on port 8000" -ForegroundColor Gray
}

# Stop Frontend Server (port 3000)
Write-Host "Checking Frontend Server (port 3000)..." -ForegroundColor Yellow
$frontendPort = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique

if ($frontendPort) {
    try {
        Stop-Process -Id $frontendPort -Force -ErrorAction Stop
        Write-Host "[OK] Frontend server stopped (port 3000)" -ForegroundColor Green
        $stopped = $true
    } catch {
        Write-Host "[WARNING] Could not stop frontend server: $_" -ForegroundColor Yellow
    }
} else {
    Write-Host "[INFO] Frontend server not running on port 3000" -ForegroundColor Gray
}

# Try to stop Python/Django processes
Write-Host "Checking for Python/Django processes..." -ForegroundColor Yellow
$pythonProcs = Get-Process python -ErrorAction SilentlyContinue | Where-Object { 
    $_.Path -like "*VALClean*backend*venv*" -or 
    $_.CommandLine -like "*manage.py runserver*" 
}

if ($pythonProcs) {
    $pythonProcs | ForEach-Object {
        try {
            Stop-Process -Id $_.Id -Force -ErrorAction Stop
            Write-Host "[OK] Stopped Python process (PID: $($_.Id))" -ForegroundColor Green
            $stopped = $true
        } catch {
            Write-Host "[WARNING] Could not stop Python process (PID: $($_.Id))" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "[INFO] No Python/Django processes found" -ForegroundColor Gray
}

# Try to stop Node/Next.js processes (be more careful - only stop Next.js dev servers)
Write-Host "Checking for Node/Next.js processes..." -ForegroundColor Yellow
$nodeProcs = Get-Process node -ErrorAction SilentlyContinue | Where-Object {
    $_.MainWindowTitle -like "*next dev*" -or
    ($_.Path -and $_.Path -like "*VALClean*frontend*")
}

if ($nodeProcs) {
    $nodeProcs | ForEach-Object {
        try {
            Stop-Process -Id $_.Id -Force -ErrorAction Stop
            Write-Host "[OK] Stopped Node process (PID: $($_.Id))" -ForegroundColor Green
            $stopped = $true
        } catch {
            Write-Host "[WARNING] Could not stop Node process (PID: $($_.Id))" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "[INFO] No Node/Next.js processes found" -ForegroundColor Gray
}

Write-Host ""
if ($stopped) {
    Write-Host "[OK] Servers stopped successfully!" -ForegroundColor Green
} else {
    Write-Host "[INFO] No servers were running" -ForegroundColor Gray
}
Write-Host ""
