# JARVIS Desktop Launcher
# Starts jarvis_wake.py headless + opens the web frontend.
# Usage: .\start_jarvis.ps1 [--gui]
param([switch]$Gui)

Set-Location "C:\Users\Free user\Jarvis"

$PY = ".\.wakevenv\Scripts\python.exe"
if (-not (Test-Path $PY)) {
    Write-Host "[ERROR] Python virtualenv not found at $PY" -ForegroundColor Red
    exit 1
}

# Ensure FastAPI/uvicorn are available
Write-Host "[JARVIS] Checking dependencies..." -ForegroundColor Cyan
foreach ($d in @("fastapi", "uvicorn")) {
    if (& $PY -c "import $($d.Replace('-', '_'))" 2>$null; $LASTEXITCODE) {
        Write-Host "[JARVIS] Installing $d ..." -ForegroundColor Yellow
        & $PY -m pip install $d --quiet
    }
}

$args = @(".\jarvis_wake.py")
if (-not $Gui) { $args += "--no-gui" }

# Start JARVIS backend as a hidden process
Write-Host "[JARVIS] Starting JARVIS backend (port 8765)..." -ForegroundColor Cyan
$proc = Start-Process -FilePath $PY -ArgumentList $args -PassThru -WindowStyle Hidden
Write-Host "[JARVIS] PID $($proc.Id)"

# Poll /health until the server binds or we time out
$ok = $false
for ($i = 0; $i -lt 30; $i++) {
    Start-Sleep -Milliseconds 600
    try {
        $r = Invoke-WebRequest -Uri "http://127.0.0.1:8765/health" -UseBasicParsing -TimeoutSec 2
        if ($r.StatusCode -eq 200) { $ok = $true; break }
    } catch { }
}
if (-not $ok) {
    Write-Host "[ERROR] Bridge did not become ready within 18s." -ForegroundColor Red
    Write-Host "       Check that nothing is already using port 8765." -ForegroundColor Yellow
    Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    exit 2
}

# Open dashboard in default browser
Write-Host "[JARVIS] Opening http://127.0.0.1:8765" -ForegroundColor Green
Start-Process "http://127.0.0.1:8765"

# Keep the launcher alive so the backend isn't orphaned
Wait-Process -Id $proc.Id
$rc = $LASTEXITCODE
if ($rc -ne 0) {
    Write-Host "[JARVIS] Exit code $rc" -ForegroundColor Yellow
}
exit $rc
