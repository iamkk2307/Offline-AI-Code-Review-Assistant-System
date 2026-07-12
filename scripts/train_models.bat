@echo off
REM ============================================================
REM Train ML Models (Run Once Before First Use)
REM ============================================================
echo [Code Review Assistant] Training ML models...
echo This takes about 60-120 seconds. Please wait...
cd /d "%~dp0"
python ml\training\train_all.py
echo.
echo Models trained! Now run start_backend.bat to start the server.
pause
