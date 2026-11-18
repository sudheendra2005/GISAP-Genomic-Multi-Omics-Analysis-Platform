@echo off
setlocal EnableExtensions

cd /d "%~dp0"

echo ================================================
echo   GISAP - Starting Local Development Environment
echo ================================================
echo.

where python >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    pause
    exit /b 1
)

where node >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH.
    pause
    exit /b 1
)

if not exist ".env" (
    if exist ".env.example" copy /Y ".env.example" ".env" >nul
)

if exist "backend\requirements.txt" (
    if not exist ".venv\Scripts\python.exe" (
        echo Creating Python virtual environment...
        python -m venv .venv
        if errorlevel 1 (
            echo ERROR: Failed to create Python virtual environment.
            pause
            exit /b 1
        )
    )

    echo Installing backend dependencies...
    ".venv\Scripts\python.exe" -m pip install --upgrade pip
    ".venv\Scripts\python.exe" -m pip install -r backend\requirements.txt
    if errorlevel 1 (
        echo ERROR: Backend dependency installation failed.
        pause
        exit /b 1
    )
)

if exist "infrastructure\docker\docker-compose.alpha.yml" (
    where docker >nul 2>&1
    if not errorlevel 1 (
        echo Starting Docker infrastructure...
        docker compose -f infrastructure\docker\docker-compose.alpha.yml up -d
    ) else (
        echo WARNING: Docker is not available; starting without Docker infrastructure.
    )
)

if exist "frontend\package.json" (
    if not exist "frontend\node_modules" (
        echo Installing frontend dependencies...
        pushd frontend
        call npm install
        popd
        if errorlevel 1 (
            echo ERROR: Frontend dependency installation failed.
            pause
            exit /b 1
        )
    )
)

echo.
 echo Starting GISAP backend on http://localhost:8000...
if exist ".venv\Scripts\python.exe" (
    start "GISAP Backend" cmd /k ".venv\Scripts\python.exe" -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
) else (
    start "GISAP Backend" cmd /k python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
)

echo Starting GISAP frontend on http://localhost:5173...
start "GISAP Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo Waiting for servers to initialize...
timeout /t 8 /nobreak >nul
start "" "http://localhost:5173"

echo.
echo GISAP is running in separate Backend and Frontend windows.
echo API documentation: http://localhost:8000/docs
echo Frontend:          http://localhost:5173
echo.
pause
endlocal
