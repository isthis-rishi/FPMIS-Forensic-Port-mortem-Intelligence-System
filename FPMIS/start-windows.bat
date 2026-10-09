@echo off
echo ============================================
echo    FPMIS - Quick Start Script (Windows)
echo ============================================
echo.

REM Check if running from project root
if not exist "backend" (
    echo ERROR: Please run this script from the FPMIS_Complete_Project directory
    pause
    exit /b 1
)

echo [1/4] Setting up Backend...
cd backend

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate

echo Installing Python dependencies...
pip install -r requirements.txt --quiet

if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env
    echo.
    echo ⚠️  IMPORTANT: Edit backend\.env with your database credentials!
    echo.
)

echo.
echo [2/4] Starting Backend Server...
start "FPMIS Backend" cmd /k "cd /d %CD% && venv\Scripts\activate && uvicorn app.main:app --reload --port 8000"

cd ..

echo.
echo [3/4] Setting up Frontend...
cd frontend

if not exist "node_modules" (
    echo Installing Node.js dependencies...
    call npm install
)

if not exist ".env.local" (
    echo Creating .env.local file...
    echo NEXT_PUBLIC_API_URL=http://localhost:8000 > .env.local
)

echo.
echo [4/4] Starting Frontend Server...
start "FPMIS Frontend" cmd /k "cd /d %CD% && npm run dev"

cd ..

echo.
echo ============================================
echo    FPMIS Started Successfully!
echo ============================================
echo.
echo    Frontend: http://localhost:3000
echo    Backend:  http://localhost:8000
echo    API Docs: http://localhost:8000/docs
echo.
echo    Press any key to close this window...
pause > nul
