"""
Shared Configuration for the 3-Laptop ICS/SCADA Cybersecurity Prototype.
SIH 2026 - System Hackers
"""
import os

# Default Network Settings
# When running across 3 laptops, change TARGET_LAPTOP_B_IP and TARGET_LAPTOP_A_IP 
# to the actual Wi-Fi / Hotspot IPv4 addresses.
DEFAULT_LAPTOP_A_IP = "127.0.0.1"   # IP of Laptop A (Protected Plant)
DEFAULT_LAPTOP_B_IP = "127.0.0.1"   # IP of Laptop B (SOC Hub & Detector)
DEFAULT_LAPTOP_C_IP = "127.0.0.1"   # IP of Laptop C (Attacker)

# Port Allocations
PORT_TELEMETRY_UDP = 5005    # Laptop A -> Laptop B (One-Way Telemetry)
PORT_PLANT_CONTROL = 5002    # Laptop C -> Laptop A (Control / Injection Channel)
PORT_TRAFFIC_TEST  = 5006    # Laptop C -> Laptop B (Network Flood / Test Traffic)

# Normal Baseline Operating Ranges
BASELINE_METRICS = {
    "turbine_rpm": {"normal_min": 2900, "normal_max": 3300, "critical_threshold": 4800, "unit": "RPM"},
    "boiler_psi":  {"normal_min": 110,  "normal_max": 145,  "critical_threshold": 280,  "unit": "PSI"},
    "reactor_temp":{"normal_min": 68.0, "normal_max": 78.0, "critical_threshold": 105.0, "unit": "°C"},
    "coolant_flow":{"normal_min": 75.0, "normal_max": 90.0, "critical_threshold": 25.0,  "unit": "L/min"},
    "grid_hz":     {"normal_min": 49.8, "normal_max": 50.2, "critical_threshold": 53.0,  "unit": "Hz"},
    "packet_rate": {"normal_min": 1,    "normal_max": 5,    "critical_threshold": 50,    "unit": "pkts/s"}
}
