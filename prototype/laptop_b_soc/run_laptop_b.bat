@echo off
cd /d "%~dp0"
title [PROJECT S.H.I.E.L.D.] - SOC Threat Defense & ML Dashboard
color 0B
echo ========================================================
echo   STARTING PROJECT S.H.I.E.L.D. : SOC DEFENSE HUB
echo   SCADA Heuristic Intrusion Evaluation & Live Defense
echo ========================================================
echo Starting Streamlit server on port 8502...
start http://localhost:8502
python -m streamlit run app.py --server.port 8502
pause
