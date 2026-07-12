@echo off
REM ============================================================
REM Start Backend Server Only (for development)
REM ============================================================
echo [Code Review Assistant] Starting Python backend...
cd /d "%~dp0"
python server\app.py --port 5000 --debug
pause
