@echo off
title SIH 2026 - 3-Laptop Localhost Demo Launcher
color 0E
echo =========================================================================
echo   SIH 2026 : 3-NODE ICS CYBERSECURITY PROTOTYPE (LOCAL ALL-IN-ONE DEMO)
echo =========================================================================
echo   Starting all 3 nodes on Localhost:
echo   - Laptop A: Plant Simulator (Port 5005 UDP)
echo   - Laptop B: SOC Threat Defense Dashboard (http://localhost:8502)
echo   - Laptop C: Attack & Traffic Console (Port 5002 / 5006)
echo =========================================================================

:: 1. Launch Laptop A in a new terminal window
start "LAPTOP A - Plant SCADA Simulator" cmd /k "cd /d %~dp0laptop_a_plant && python plant_sim.py"

:: 2. Launch Laptop B SOC Streamlit Dashboard
start "LAPTOP B - SOC Defense Dashboard" cmd /k "cd /d %~dp0laptop_b_soc && python -m streamlit run app.py --server.port 8502"

:: 3. Launch Laptop C Attack Console
start "LAPTOP C - Attack Simulator" cmd /k "cd /d %~dp0laptop_c_attacker && python attack_console.py"

echo.
echo All 3 modules launched in separate windows!
echo Opening browser to http://localhost:8502 ...
start http://localhost:8502
echo.
pause
