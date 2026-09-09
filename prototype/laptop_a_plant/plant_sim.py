"""
=============================================================================
 LAPTOP A : INDUSTRIAL SCADA/PLC SIMULATOR WITH CREDENTIAL AUTHENTICATION
 SIH 2026 - System Hackers Prototype
=============================================================================
- Holds industrial setpoints & protected credentials (admin_plc / SCADA_KEY_9921).
- Emits continuous UDP telemetry + authentication audit stream to Laptop B.
- Listens on Port 5002 for authentication & control requests from Laptop C.
"""

import sys
import os
import time
import json
import socket
import random
import threading
from datetime import datetime

# Allow importing config from parent folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
try:
    from config import PORT_TELEMETRY_UDP, PORT_PLANT_CONTROL, DEFAULT_LAPTOP_B_IP
except ImportError:
    PORT_TELEMETRY_UDP = 5005
    PORT_PLANT_CONTROL = 5002
    DEFAULT_LAPTOP_B_IP = "127.0.0.1"


# Protected Master Credentials of Laptop A (What Laptop C targets)
VALID_USER = "admin_plc"
VALID_KEY = "SCADA_KEY_9921"


class IndustrialPlantSimulator:
    def __init__(self, target_soc_ip=DEFAULT_LAPTOP_B_IP):
        self.target_soc_ip = target_soc_ip
        self.running = True
        self.lock = threading.Lock()
        
        # Physical & Security State
        self.state = {
            "turbine_rpm": 3000.0,
            "boiler_psi": 125.0,
            "reactor_temp": 72.5,
            "coolant_flow": 82.0,
            "grid_hz": 50.0,
            "valve_open_pct": 85.0,
            "status": "NORMAL_OPERATING",
            
            # Credential & Authentication State
            "active_user": "LOCAL_OPERATOR",
            "auth_status": "AUTHENTICATED_LOCAL",
            "failed_login_count": 0,
            "last_login_attempt": "None",
            "last_incident": "Plant Operating in Secure Baseline",
            "tampered_by": "None",
            "packets_sent": 0
        }
        
        # Attack injection targets
        self.target_override = {
            "active": False,
            "turbine_rpm": 3000.0,
            "boiler_psi": 125.0,
            "reactor_temp": 72.5,
            "coolant_flow": 82.0
        }

    def command_listener(self):
        """Listens for Authentication & PLC commands from Laptop C."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("0.0.0.0", PORT_PLANT_CONTROL))
            while self.running:
                data, addr = sock.recvfrom(2048)
                try:
                    payload = json.loads(data.decode("utf-8"))
                    req_type = payload.get("type", "COMMAND")
                    username = payload.get("username", "")
                    secret_key = payload.get("secret_key", "")
                    sender = f"{addr[0]}"
                    
                    with self.lock:
                        # 1. Credential Validation Check
                        is_auth_valid = (username == VALID_USER and secret_key == VALID_KEY)
                        
                        if req_type == "LOGIN_ATTEMPT":
                            if is_auth_valid:
                                self.state["auth_status"] = "COMPROMISED_CREDENTIAL_LOGIN"
                                self.state["active_user"] = username
                                self.state["tampered_by"] = sender
                                self.state["last_login_attempt"] = f"CRACKED by {sender} ({username})"
                                self.state["last_incident"] = f"UNAUTHORIZED CREDENTIAL LOGIN: {username} authenticated from untrusted IP {sender}"
                            else:
                                self.state["failed_login_count"] += 1
                                self.state["auth_status"] = "FAILED_AUTH_ATTEMPT"
                                self.state["last_login_attempt"] = f"FAILED attempt: '{username}':'{secret_key}' from {sender}"
                                self.state["last_incident"] = f"FAILED LOGIN #{self.state['failed_login_count']} from {sender}"
                                
                        elif req_type == "MALICIOUS_OVERRIDE":
                            if is_auth_valid:
                                cmd = payload.get("command", "")
                                self.state["auth_status"] = "PRIVILEGED_COMMAND_EXECUTED"
                                self.state["active_user"] = username
                                self.state["tampered_by"] = sender
                                
                                if cmd == "OVERRIDE_TURBINE_RPM":
                                    rpm = float(payload.get("target_rpm", 5850.0))
                                    self.target_override["active"] = True
                                    self.target_override["turbine_rpm"] = rpm
                                    self.state["status"] = "CRITICAL_TURBINE_OVERSPEED"
                                    self.state["last_incident"] = f"STOLEN CREDENTIAL ATTACK: {username} forced Turbine to {rpm} RPM"
                                    
                                elif cmd == "OVERPRESSURE_BOILER":
                                    psi = float(payload.get("target_psi", 420.0))
                                    self.target_override["active"] = True
                                    self.target_override["boiler_psi"] = psi
                                    self.state["status"] = "CRITICAL_BOILER_OVERPRESSURE"
                                    self.state["last_incident"] = f"STOLEN CREDENTIAL ATTACK: {username} spiked Boiler to {psi} PSI"
                                    
                                elif cmd == "CHOKE_COOLANT":
                                    self.target_override["active"] = True
                                    self.target_override["coolant_flow"] = 4.0
                                    self.target_override["reactor_temp"] = 125.0
                                    self.state["status"] = "THERMAL_RUNAWAY_ALERT"
                                    self.state["last_incident"] = f"STOLEN CREDENTIAL ATTACK: {username} choked coolant flow"
                            else:
                                self.state["failed_login_count"] += 1
                                self.state["auth_status"] = "UNAUTHORIZED_COMMAND_REJECTED"
                                self.state["last_incident"] = f"REJECTED Command: Invalid credentials from {sender}"
                                
                        elif req_type == "EMERGENCY_SHUTDOWN":
                            self.target_override["active"] = True
                            self.target_override["turbine_rpm"] = 0.0
                            self.target_override["boiler_psi"] = 0.0
                            self.target_override["reactor_temp"] = 25.0
                            self.target_override["coolant_flow"] = 0.0
                            self.state["status"] = "EMERGENCY_SHUTDOWN_OFFLINE"
                            self.state["auth_status"] = "SERVER_OFFLINE_TRIPPED"
                            self.state["active_user"] = "NONE (POWERED_OFF)"
                            self.state["tampered_by"] = f"SOC_SAFETY_TRIP ({sender})"
                            self.state["last_incident"] = f"🚨 EMERGENCY KILL-SWITCH ACTIVATED BY SOC ({sender}) -> SERVER POWERED OFF!"
                            
                        elif req_type == "RESET_NORMAL" or req_type == "SERVER_POWER_ON":
                            self.target_override["active"] = False
                            self.state["status"] = "NORMAL_OPERATING"
                            self.state["auth_status"] = "AUTHENTICATED_LOCAL"
                            self.state["active_user"] = "LOCAL_OPERATOR"
                            self.state["failed_login_count"] = 0
                            self.state["last_incident"] = "Plant safely brought back online to baseline"
                            self.state["tampered_by"] = "None"
                            
                except Exception:
                    pass
        except Exception as e:
            print(f"[!] Command listener error: {e}")
        finally:
            sock.close()

    def physics_loop(self):
        """Simulates physical plant dynamics."""
        while self.running:
            with self.lock:
                if self.target_override["active"]:
                    self.state["turbine_rpm"] += (self.target_override.get("turbine_rpm", 3000.0) - self.state["turbine_rpm"]) * 0.35
                    self.state["boiler_psi"] += (self.target_override.get("boiler_psi", 125.0) - self.state["boiler_psi"]) * 0.35
                    self.state["reactor_temp"] += (self.target_override.get("reactor_temp", 72.5) - self.state["reactor_temp"]) * 0.25
                    self.state["coolant_flow"] += (self.target_override.get("coolant_flow", 82.0) - self.state["coolant_flow"]) * 0.35
                else:
                    self.state["turbine_rpm"] = 3000.0 + random.uniform(-12.0, 15.0)
                    self.state["boiler_psi"] = 125.0 + random.uniform(-1.5, 1.8)
                    self.state["reactor_temp"] = 72.5 + random.uniform(-0.4, 0.4)
                    self.state["coolant_flow"] = 82.0 + random.uniform(-0.8, 1.0)
                    self.state["grid_hz"] = 50.0 + random.uniform(-0.03, 0.03)
                    self.state["valve_open_pct"] = 85.0 + random.uniform(-0.4, 0.4)
            time.sleep(0.5)

    def telemetry_broadcaster(self):
        """Broadcasts telemetry + authentication state to Laptop B."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while self.running:
            with self.lock:
                telemetry = {
                    "source": "LAPTOP_A_SCADA_PLC",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    # Physical Metrics
                    "turbine_rpm": round(self.state["turbine_rpm"], 2),
                    "boiler_psi": round(self.state["boiler_psi"], 2),
                    "reactor_temp": round(self.state["reactor_temp"], 2),
                    "coolant_flow": round(self.state["coolant_flow"], 2),
                    "grid_hz": round(self.state["grid_hz"], 3),
                    "plant_status": self.state["status"],
                    # Security & Authentication State
                    "active_user": self.state["active_user"],
                    "auth_status": self.state["auth_status"],
                    "failed_login_count": self.state["failed_login_count"],
                    "last_login_attempt": self.state["last_login_attempt"],
                    "last_incident": self.state["last_incident"],
                    "tampered_by": self.state["tampered_by"],
                    "seq_num": self.state["packets_sent"] + 1
                }
                self.state["packets_sent"] += 1
                
            try:
                data = json.dumps(telemetry).encode("utf-8")
                sock.sendto(data, (self.target_soc_ip, PORT_TELEMETRY_UDP))
            except Exception:
                pass
            time.sleep(0.35)
        sock.close()

    def print_status_screen(self):
        """Displays real-time plant and authentication monitor."""
        while self.running:
            os.system('cls' if os.name == 'nt' else 'clear')
            with self.lock:
                rpm = self.state["turbine_rpm"]
                psi = self.state["boiler_psi"]
                temp = self.state["reactor_temp"]
                flow = self.state["coolant_flow"]
                status = self.state["status"]
                user = self.state["active_user"]
                auth_st = self.state["auth_status"]
                fails = self.state["failed_login_count"]
                incident = self.state["last_incident"]
                target_ip = self.target_soc_ip
                pkts = self.state["packets_sent"]

            print("=" * 80)
            print("   LAPTOP A : INDUSTRIAL PLANT (SCADA/PLC) & ACCESS GATEWAY")
            print("=" * 80)
            print(f" Target SOC Receiver (Laptop B) : {target_ip}:{PORT_TELEMETRY_UDP}")
            print(f" Protected Credentials          : User='{VALID_USER}' | Key='{VALID_KEY}'")
            print(f" Current Active User Session    : [{user}] -> Status: {auth_st}")
            print(f" Failed Login Counter           : {fails}")
            print(f" Telemetry Packets Broadcasted  : {pkts}")
            print("-" * 80)
            print(f" [1] Turbine Speed    : {rpm:7.1f} RPM   {'[OVER-SPEED!]' if rpm > 4500 else '[NORMAL]'}")
            print(f" [2] Steam Boiler     : {psi:7.1f} PSI   {'[OVERPRESSURE!]' if psi > 250 else '[NORMAL]'}")
            print(f" [3] Reactor Core     : {temp:7.1f} deg C {'[OVERHEAT!]' if temp > 100 else '[NORMAL]'}")
            print(f" [4] Coolant Valve    : {flow:7.1f} L/min {'[CHOKED!]' if flow < 30 else '[NORMAL]'}")
            print("-" * 80)
            print(f" Last Security Event  : {incident}")
            print("=" * 80)
            print(" >> Emitting live telemetry to Laptop B every 1.0s...")
            print(" >> Press Ctrl+C to stop.")
            time.sleep(1.0)


def main():
    print("=" * 70)
    print(" LAPTOP A - INDUSTRIAL PLANT & ACCESS GATEWAY STARTUP")
    print("=" * 70)
    
    target_ip = DEFAULT_LAPTOP_B_IP
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        target_ip = sys.argv[1]
    else:
        try:
            user_ip = input(f"Enter Laptop B (SOC) IP address [Press Enter for {DEFAULT_LAPTOP_B_IP}]: ").strip()
            if user_ip:
                target_ip = user_ip
        except (EOFError, KeyboardInterrupt):
            target_ip = DEFAULT_LAPTOP_B_IP

    sim = IndustrialPlantSimulator(target_soc_ip=target_ip)
    
    t_cmd = threading.Thread(target=sim.command_listener, daemon=True)
    t_phy = threading.Thread(target=sim.physics_loop, daemon=True)
    t_tel = threading.Thread(target=sim.telemetry_broadcaster, daemon=True)
    
    t_cmd.start()
    t_phy.start()
    t_tel.start()
    
    try:
        sim.print_status_screen()
    except KeyboardInterrupt:
        print("\n[*] Shutting down Plant Simulator...")
        sim.running = False


if __name__ == "__main__":
    main()
