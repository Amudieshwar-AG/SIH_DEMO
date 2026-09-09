"""
=============================================================================
 LAPTOP C : TRAFFIC & ATTACK SIMULATOR (INTERACTIVE TERMINAL CONSOLE)
 SIH 2026 - System Hackers Prototype
=============================================================================
Provides instant trigger menus for:
 [1] Normal Plant Baseline
 [2] Stuxnet Turbine Over-speed Attack (Targets Laptop A)
 [3] Boiler Overpressure & Valve Tampering (Targets Laptop A)
 [4] Coolant Starvation & Thermal Runaway (Targets Laptop A)
 [5] Volumetric UDP DDoS Flood (Targets Laptop B)
 [6] Stealth Port Scan Reconnaissance (Targets Laptop A/B)
"""

import socket
import json
import time
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
try:
    from config import PORT_PLANT_CONTROL, PORT_TRAFFIC_TEST, DEFAULT_LAPTOP_A_IP, DEFAULT_LAPTOP_B_IP
except ImportError:
    PORT_PLANT_CONTROL = 5002
    PORT_TRAFFIC_TEST = 5006
    DEFAULT_LAPTOP_A_IP = "127.0.0.1"
    DEFAULT_LAPTOP_B_IP = "127.0.0.1"


def send_plant_command(target_a_ip, command_dict):
    """Sends malicious control payload to Laptop A's PLC Port."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        data = json.dumps(command_dict).encode("utf-8")
        sock.sendto(data, (target_a_ip, PORT_PLANT_CONTROL))
        print(f"\n[+] Malicious PLC Command Sent to Plant ({target_a_ip}:{PORT_PLANT_CONTROL}):\n    -> {command_dict}")
    except Exception as e:
        print(f"[-] Error sending command: {e}")
    finally:
        sock.close()


def send_traffic_flood(target_b_ip, duration_sec=5, pps=50):
    """Sends high-volume UDP attack traffic to Laptop B's SOC collector."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"\n[*] Launching Volumetric UDP Flood -> {target_b_ip}:{PORT_TRAFFIC_TEST} for {duration_sec}s...")
    start_time = time.time()
    count = 0
    
    payload = json.dumps({
        "attack_type": "VOLUMETRIC_FLOOD",
        "description": "High-rate UDP sensor jamming attack",
        "timestamp": time.time()
    }).encode("utf-8")

    while time.time() - start_time < duration_sec:
        try:
            sock.sendto(payload, (target_b_ip, PORT_TRAFFIC_TEST))
            count += 1
            time.sleep(1.0 / pps)
        except Exception:
            pass
            
    sock.close()
    print(f"[+] UDP Flood Complete! Fired {count} packets at Laptop B.")


def run_port_scan(target_ip, ports=[5000, 5001, 5002, 5005, 5006, 8501, 8502]):
    """Simulates reconnaissance port sweep."""
    print(f"\n[*] Initiating Reconnaissance Port Sweep on {target_ip}...")
    for port in ports:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.3)
        res = s.connect_ex((target_ip, port))
        status = "OPEN" if res == 0 else "FILTERED / CLOSED"
        print(f"    -> Port {port:5d} : {status}")
        s.close()
        time.sleep(0.1)
    print("[+] Port Sweep Complete.")


def main():
    print("=" * 70)
    print(" LAPTOP C - THREAT & ATTACK SIMULATOR CONSOLE")
    print("=" * 70)
    
    user_a = input(f"Enter Laptop A (Plant) IP [Enter for {DEFAULT_LAPTOP_A_IP}]: ").strip()
    target_a_ip = user_a if user_a else DEFAULT_LAPTOP_A_IP

    user_b = input(f"Enter Laptop B (SOC) IP   [Enter for {DEFAULT_LAPTOP_B_IP}]: ").strip()
    target_b_ip = user_b if user_b else DEFAULT_LAPTOP_B_IP

    while True:
        print("\n" + "=" * 70)
        print(f" TARGET PLANT (Laptop A): {target_a_ip}:{PORT_PLANT_CONTROL}")
        print(f" TARGET SOC   (Laptop B): {target_b_ip}:{PORT_TRAFFIC_TEST}")
        print("=" * 70)
        print(" [1] [NORMAL] Send Safe / Normal Baseline (Reset Plant)")
        print(" [2] [ATTACK] Stuxnet Turbine Over-speed (Rev to 5,800 RPM)")
        print(" [3] [ATTACK] Boiler Overpressure & Valve Lock (Spike to 420 PSI)")
        print(" [4] [ATTACK] Coolant Starvation & Core Thermal Runaway")
        print(" [5] [ATTACK] Volumetric UDP Flood / DDoS on Laptop B")
        print(" [6] [ATTACK] Stealth Reconnaissance Port Scan")
        print(" [0] [EXIT]   Exit Console")
        print("=" * 70)
        
        choice = input("Enter choice [0-6]: ").strip()
        
        if choice == "1":
            send_plant_command(target_a_ip, {"command": "RESET_NORMAL"})
        elif choice == "2":
            send_plant_command(target_a_ip, {"command": "OVERRIDE_TURBINE_RPM", "target_rpm": 5850.0})
        elif choice == "3":
            send_plant_command(target_a_ip, {"command": "OVERPRESSURE_BOILER", "target_psi": 420.0})
        elif choice == "4":
            send_plant_command(target_a_ip, {"command": "CHOKE_COOLANT"})
        elif choice == "5":
            send_traffic_flood(target_b_ip, duration_sec=5, pps=60)
        elif choice == "6":
            run_port_scan(target_a_ip)
        elif choice == "0":
            print("\n[*] Exiting Attacker Console.")
            break
        else:
            print("[!] Invalid option. Please select 0-6.")
        
        time.sleep(1)


if __name__ == "__main__":
    main()
