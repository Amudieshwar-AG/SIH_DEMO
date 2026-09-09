@echo off
cd /d "%~dp0"
title [LAPTOP C] - Cyber Threat & Attack Simulator
color 0C
echo ========================================================
echo   STARTING LAPTOP C: THREAT & TRAFFIC SIMULATOR
echo ========================================================
echo 1. Interactive Terminal Console (Fastest)
echo 2. Web Cyber Weapon Dashboard (Streamlit)
echo ========================================================
set /p choice="Select Mode [1 or 2, default is 1]: "

if "%choice%"=="2" (
    start http://localhost:8503
    python -m streamlit run attacker_ui.py --server.port 8503
) else (
    python attack_console.py
)
pause
