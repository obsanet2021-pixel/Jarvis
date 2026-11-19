@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  start "JARVIS server" /min py -m http.server 8000
) else (
  where python >nul 2>nul
  if errorlevel 1 (
    echo Python 3 was not found. Install Python or run: python -m http.server 8000
    pause
    exit /b 1
  )
  start "JARVIS server" /min python -m http.server 8000
)
timeout /t 2 /nobreak >nul
start "" http://localhost:8000
