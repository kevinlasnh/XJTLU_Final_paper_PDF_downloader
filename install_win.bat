@echo off
REM XJTLU PDF Downloader - Windows Installation Script
echo ==========================================
echo XJTLU PDF Downloader - Windows Setup
echo ==========================================

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python found

REM Install dependencies
echo.
echo [INFO] Installing dependencies...
pip install -r requirements.txt

REM Install Playwright browsers
echo.
echo [INFO] Installing Chromium browser for Playwright...
python -m playwright install chromium

echo.
echo ==========================================
echo [OK] Installation complete!
echo.
echo To run the application:
echo   python main.py
echo   or double-click run_win.bat
echo ==========================================
pause
