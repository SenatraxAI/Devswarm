@echo off
echo ========================================
echo DevSwarm Backend Startup
echo ========================================
echo.

REM Check if Ollama is running
echo [1/4] Checking Ollama...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Ollama is NOT running!
    echo    Please start Ollama first: ollama serve
    pause
    exit /b 1
)
echo ✅ Ollama is running

REM Check if gemma3:4b exists
echo.
echo [2/4] Checking for Gemma 3:4b model...
ollama list | findstr "gemma3:4b" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  gemma3:4b not found
    echo    Available models:
    ollama list
    echo.
    set /p CHOICE="Use llama3.2:3b instead? (y/n): "
    if /i "%CHOICE%"=="y" (
        echo Using llama3.2:3b...
        REM Could update model_manager.py here
    ) else (
        echo Please download gemma3:4b first: ollama pull gemma3:4b
        pause
        exit /b 1
    )
) else (
    echo ✅ gemma3:4b found
)

REM Start backend
echo.
echo [3/4] Starting FastAPI backend...
echo.
cd /d "%~dp0"
python main.py

pause
