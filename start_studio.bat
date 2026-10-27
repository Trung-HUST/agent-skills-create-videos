@echo off
title AG Local AI Video Production Studio (RTX 5060 Deck)
cd /d "%~dp0"
echo ============================================================
echo   AG LOCAL AI VIDEO STUDIO - STARTING SERVER...
echo   Opening http://127.0.0.1:8080 in your browser
echo ============================================================
start "" "http://127.0.0.1:8080"
python studio_server.py --host 127.0.0.1 --port 8080
pause
