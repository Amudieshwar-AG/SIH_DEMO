@echo off
cd /d "%~dp0"
title [LAPTOP B] - SOC Threat Defense & ML Dashboard
color 0B
echo ========================================================
echo   STARTING LAPTOP B: SOC THREAT DEFENSE DASHBOARD
echo ========================================================
echo Starting Streamlit server on port 8502...
start http://localhost:8502
python -m streamlit run app.py --server.port 8502
pause
