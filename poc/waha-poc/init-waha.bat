@echo off
cd /d "%~dp0"
if not exist waha-env mkdir waha-env
echo Generating WAHA credentials into waha-env\.env ...
docker run --rm -v "%CD%\waha-env:/app/env" devlikeapro/waha init-waha /app/env
echo.
echo 1. Copy WAHA_API_KEY from waha-env\.env into your Flask .env
echo 2. docker compose down
echo 3. docker compose up -d
echo 4. Restart python app.py
pause
