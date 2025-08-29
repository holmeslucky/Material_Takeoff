@echo off
echo Capitol Engineering - Takeoff Application Development Startup
echo ================================================================

REM Check if .env file exists
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo.
    echo IMPORTANT: Please set your OpenAI API key as environment variable
    echo For production: Set OPENAI_API_KEY in Railway environment variables
    echo For development: Set OPENAI_API_KEY in your local environment
    echo.
    pause
)

echo Starting development environment...
echo.

REM Check if Docker is running
docker info >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

echo Building and starting services...
docker-compose up --build -d

echo.
echo Services starting up...
echo - Frontend: http://localhost:7000
echo - Backend API: http://localhost:8000
echo - Full App (Nginx): http://localhost:80
echo - Database: localhost:5432
echo.

echo Waiting for services to be ready...
timeout /t 10 /nobreak >nul

REM Check service health
echo Checking service status...
docker-compose ps

echo.
echo Development environment ready!
echo.
echo Useful commands:
echo - View logs: docker-compose logs -f
echo - Stop services: docker-compose down
echo - Rebuild: docker-compose up --build
echo.
pause