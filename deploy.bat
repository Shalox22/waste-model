@echo off
REM Trash Detection API - Docker Deployment Script for Windows
REM Usage: deploy.bat start|stop|restart|logs|build|clean|status

setlocal enabledelayedexpansion

set PROJECT_NAME=trash-detector
set IMAGE_NAME=trash-detector:latest

echo.
echo ================================
echo Trash Detection API - Docker
echo ================================
echo.

if "%1"=="" goto start
if "%1"=="start" goto start
if "%1"=="stop" goto stop
if "%1"=="restart" goto restart
if "%1"=="logs" goto logs
if "%1"=="build" goto build
if "%1"=="clean" goto clean
if "%1"=="status" goto status
goto usage

:start
echo Starting Docker containers...
docker-compose up -d
echo ✓ API started! Access it at http://localhost:8080
echo ✓ API documentation: http://localhost:8080/docs
goto end

:stop
echo Stopping Docker containers...
docker-compose down
echo ✓ Containers stopped
goto end

:restart
echo Restarting Docker containers...
docker-compose down
docker-compose up -d
echo ✓ Containers restarted
goto end

:logs
echo Showing container logs (Ctrl+C to exit)...
docker-compose logs -f trash-detector
goto end

:build
echo Building Docker image...
docker build -t %IMAGE_NAME% .
echo ✓ Image built successfully
goto end

:clean
echo Cleaning up Docker resources...
docker-compose down -v
docker rmi %IMAGE_NAME%
echo ✓ Cleanup complete
goto end

:status
echo Checking container status...
docker-compose ps
goto end

:usage
echo Usage: deploy.bat [start^|stop^|restart^|logs^|build^|clean^|status]
echo.
echo Commands:
echo   start   - Start the API server
echo   stop    - Stop the API server
echo   restart - Restart the API server
echo   logs    - View container logs
echo   build   - Build the Docker image
echo   clean   - Remove all containers and images
echo   status  - Show container status
echo.
echo If no command is specified, 'start' is used by default.
goto end

:end
