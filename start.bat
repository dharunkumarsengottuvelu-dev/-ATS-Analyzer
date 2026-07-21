@echo off
title ATS Resume Analyzer - Launcher
echo ============================================
echo    ATS Resume Analyzer - Starting Up
echo ============================================
echo.

:: Step 1: Kill existing processes on ports 8000 and 3000
echo [1/4] Cleaning up old processes on ports 8000 and 3000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000 "' ) do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3000 "' ) do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3001 "' ) do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3002 "' ) do taskkill /F /PID %%a >nul 2>&1
echo     Done.
echo.

:: Step 2: Start Backend API (cmd /k uses CMD, not PowerShell - backslash paths work fine)
echo [2/4] Starting Backend API on http://127.0.0.1:8000 ...
start "ATS Backend API" cmd /k "cd /d %~dp0 && backend\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000"
echo     Done.
echo.

:: Step 3: Wait for backend to start
echo [3/4] Waiting 5 seconds for backend to initialize...
timeout /t 5 /nobreak >nul
echo     Done.
echo.

:: Step 4: Start Frontend
echo [4/4] Starting Frontend on http://localhost:3000 ...
start "ATS Frontend UI" cmd /k "cd /d %~dp0frontend && npm run dev"
echo     Done.
echo.

echo ============================================
echo  Application is running!
echo  Backend  : http://127.0.0.1:8000
echo  Frontend : http://localhost:3000
echo  API Docs : http://127.0.0.1:8000/docs
echo ============================================
echo.
pause
