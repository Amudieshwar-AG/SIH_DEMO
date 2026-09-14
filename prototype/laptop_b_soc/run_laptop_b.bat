@echo off
cd /d "%~dp0"
title [PROJECT SYSTEM HACKERS] - SOC Threat Defense & ML Dashboard
color 0B
echo ========================================================
echo   STARTING PROJECT SYSTEM HACKERS : SOC DEFENSE HUB
echo   SCADA Cyber Defense & AI SOC Hub
echo ========================================================
echo Starting Streamlit server on port 8502...
start http://localhost:8502
python -m streamlit run app.py --server.port 8502
pause
