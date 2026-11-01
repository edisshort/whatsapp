@echo off
cd /d "%~dp0"
if not exist .env copy .env.example .env
pip install -r requirements.txt -q
echo Start Evolution: docker compose up -d
echo Start app:       python app.py
echo Open http://127.0.0.1:5002  admin / admin123
pause
