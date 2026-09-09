"""
=============================================================================
 LAPTOP C : CREDENTIAL HACKER & THREAT INJECTOR CONSOLE
 SIH 2026 - System Hackers Prototype
=============================================================================
Demonstrates:
 [1] Normal Plant Baseline (Reset)
 [2] Credential Brute-Force Attack against Laptop A (Dictionary Attack)
 [3] Stolen Credential Exploit -> Turbine Over-speed (5,850 RPM)
 [4] Stolen Credential Exploit -> Boiler Overpressure (420 PSI)
 [5] Stolen Credential Exploit -> Coolant Pump Choke
"""

import socket
import json
import time
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
try:
    from config import PORT_PLANT_CONTROL, DEFAULT_LAPTOP_A_IP
except ImportError:
    PORT_PLANT_CONTROL = 5002
    DEFAULT_LAPTOP_A_IP = "127.0.0.1"

# Known target credentials on Laptop A
TARGET_USER = "admin_plc"
STOLEN_KEY  = "SCADA_KEY_9921"


def send_packet(target_ip, payload):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        data = json.dumps(payload).encode("utf-8")
        sock.sendto(data, (target_ip, PORT_PLANT_CONTROL))
    except Exception as e:
        print(f"[-] Transmission error: {e}")
    finally:
        sock.close()


def run_bruteforce_attack(target_ip):
    """Sends a rapid dictionary of bad credentials against Laptop A."""
    print(f"\n[*] Launching Credential Brute-Force Dictionary Attack -> {target_ip}:{PORT_PLANT_CONTROL}...")
    wordlist = [
        ("admin", "123456"),
        ("root", "toor"),
        ("operator", "scada2026"),
        ("admin_plc", "wrong_key_110"),
        ("admin_plc", "guest_key_77")
    ]
    for user, pwd in wordlist:
        print(f"    -> [TRYING] User: '{user}' | Key: '{pwd}' ... REJECTED (401)")
        send_packet(target_ip, {
            "type": "LOGIN_ATTEMPT",
            "username": user,
            "secret_key": pwd
        })
        time.sleep(0.4)
    print("[!] 5 Failed Login attempts logged on Laptop A. Alert triggered on Laptop B!")


def run_credential_override(target_ip, attack_type):
    """Uses valid stolen credentials to hijack PLC and manipulate physical process."""
    if attack_type == "TURBINE":
        print(f"\n[+] Authenticating as '{TARGET_USER}' using Stolen Key '{STOLEN_KEY}'...")
        print("[!] [EXPLOIT] Injecting unauthorized setpoint: Turbine RPM = 5,850 RPM")
        send_packet(target_ip, {
            "type": "MALICIOUS_OVERRIDE",
            "username": TARGET_USER,
            "secret_key": STOLEN_KEY,
            "command": "OVERRIDE_TURBINE_RPM",
            "target_rpm": 5850.0
        })
    elif attack_type == "BOILER":
        print(f"\n[+] Authenticating as '{TARGET_USER}' using Stolen Key '{STOLEN_KEY}'...")
        print("[!] [EXPLOIT] Injecting unauthorized setpoint: Boiler PSI = 420 PSI")
        send_packet(target_ip, {
            "type": "MALICIOUS_OVERRIDE",
            "username": TARGET_USER,
            "secret_key": STOLEN_KEY,
            "command": "OVERPRESSURE_BOILER",
            "target_psi": 420.0
        })
    elif attack_type == "COOLANT":
        print(f"\n[+] Authenticating as '{TARGET_USER}' using Stolen Key '{STOLEN_KEY}'...")
        print("[!] [EXPLOIT] Injecting unauthorized pump choke command")
        send_packet(target_ip, {
            "type": "MALICIOUS_OVERRIDE",
            "username": TARGET_USER,
            "secret_key": STOLEN_KEY,
            "command": "CHOKE_COOLANT"
        })


def main():
    print("=" * 70)
    print(" LAPTOP C - CREDENTIAL HACKER & THREAT INJECTOR")
    print("=" * 70)
    
    target_ip = DEFAULT_LAPTOP_A_IP
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        target_ip = sys.argv[1]
    else:
        try:
            user_a = input(f"Enter Laptop A (Plant) IP [Enter for {DEFAULT_LAPTOP_A_IP}]: ").strip()
            if user_a:
                target_ip = user_a
        except (EOFError, KeyboardInterrupt):
            target_ip = DEFAULT_LAPTOP_A_IP

    while True:
        print("\n" + "=" * 70)
        print(f" TARGET PLANT (Laptop A): {target_ip}:{PORT_PLANT_CONTROL}")
        print(f" TARGET USER ACCOUNT    : {TARGET_USER}")
        print("=" * 70)
        print(" [1] [NORMAL]      Restore Plant & Revoke Attacker Session")
        print(" [2] [BRUTE-FORCE] Credential Stuffing / Dictionary Attack")
        print(" [3] [EXPLOIT]     Stolen Credential -> Force Turbine Over-speed (5,850 RPM)")
        print(" [4] [EXPLOIT]     Stolen Credential -> Spike Boiler Overpressure (420 PSI)")
        print(" [5] [EXPLOIT]     Stolen Credential -> Choke Coolant Pump")
        print(" [0] [EXIT]        Exit Console")
        print("=" * 70)
        
        try:
            choice = input("Enter choice [0-5]: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
            
        if choice == "1":
            send_packet(target_ip, {"type": "RESET_NORMAL"})
            print("[+] Plant restored to normal baseline.")
        elif choice == "2":
            run_bruteforce_attack(target_ip)
        elif choice == "3":
            run_credential_override(target_ip, "TURBINE")
        elif choice == "4":
            run_credential_override(target_ip, "BOILER")
        elif choice == "5":
            run_credential_override(target_ip, "COOLANT")
        elif choice == "0":
            print("[*] Exiting Console.")
            break
        else:
            print("[!] Invalid choice. Please choose 0-5.")
            
        time.sleep(1)


if __name__ == "__main__":
    main()
