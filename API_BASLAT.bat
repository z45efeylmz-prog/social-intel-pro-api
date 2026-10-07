@echo off
title SocialIntel Pro API Engine
color 0B
echo ===================================================
echo     SOCIALINTEL PRO API - MICRO-API ENGINE
echo ===================================================
echo.
echo [*] API Baslatiliyor...
echo [*] Swagger UI: http://127.0.0.1:8000/docs
echo [*] ReDoc:      http://127.0.0.1:8000/redoc
echo.
python -m uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
pause
