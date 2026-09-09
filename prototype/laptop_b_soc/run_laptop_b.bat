@echo off
title [LAPTOP B] - SOC Threat Defense & ML Dashboard
color 0B
echo ========================================================
echo   STARTING LAPTOP B: SOC THREAT DEFENSE DASHBOARD
echo ========================================================
python -m streamlit run app.py --server.port 8502
pause
