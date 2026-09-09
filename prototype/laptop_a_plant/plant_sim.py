"""
=============================================================================
 LAPTOP A : PROTECTED SIDE - INDUSTRIAL PLANT / SCADA & PLC SIMULATOR
 SIH 2026 - System Hackers Prototype
=============================================================================
- Simulates physical processes: Turbine, Steam Boiler, Reactor Core, Coolant Valve.
- Emits one-way UDP telemetry packets to Laptop B (SOC Hub).
- Listens on Port 5002 for PLC commands (which Laptop C can exploit).
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


class IndustrialPlantSimulator:
    def __init__(self, target_soc_ip=DEFAULT_LAPTOP_B_IP):
        self.target_soc_ip = target_soc_ip
        self.running = True
        self.lock = threading.Lock()
        
        # Plant Physical State (Normal Baseline)
        self.state = {
            "turbine_rpm": 3000.0,
            "boiler_psi": 125.0,
            "reactor_temp": 72.5,
            "coolant_flow": 82.0,
            "grid_hz": 50.0,
            "valve_open_pct": 85.0,
            "status": "NORMAL_OPERATING",
            "last_incident": "None (Plant Secure)",
            "safety_interlock": "ARMED",
            "packets_sent": 0,
            "tampered_by": "None"
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
        """Listens for PLC commands from network (e.g. Laptop C attack injector)."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("0.0.0.0", PORT_PLANT_CONTROL))
            while self.running:
                data, addr = sock.recvfrom(2048)
                try:
                    payload = json.loads(data.decode("utf-8"))
                    cmd = payload.get("command", "")
                    sender = f"{addr[0]}:{addr[1]}"
                    
                    with self.lock:
                        if cmd == "OVERRIDE_TURBINE_RPM":
                            rpm = float(payload.get("target_rpm", 5600.0))
                            self.target_override["active"] = True
                            self.target_override["turbine_rpm"] = rpm
                            self.state["status"] = "CRITICAL_TURBINE_OVERSPEED"
                            self.state["last_incident"] = f"UNAUTHORIZED PLC OVERRIDE from {sender} -> RPM: {rpm}"
                            self.state["tampered_by"] = sender
                            
                        elif cmd == "OVERPRESSURE_BOILER":
                            psi = float(payload.get("target_psi", 380.0))
                            self.target_override["active"] = True
                            self.target_override["boiler_psi"] = psi
                            self.target_override["valve_open_pct"] = 10.0
                            self.state["status"] = "CRITICAL_BOILER_OVERPRESSURE"
                            self.state["last_incident"] = f"VALVE LOCKED & PRESSURE SPIKE from {sender} -> PSI: {psi}"
                            self.state["tampered_by"] = sender
                            
                        elif cmd == "CHOKE_COOLANT":
                            self.target_override["active"] = True
                            self.target_override["coolant_flow"] = 4.0
                            self.target_override["reactor_temp"] = 128.0
                            self.state["status"] = "THERMAL_RUNAWAY_ALERT"
                            self.state["last_incident"] = f"COOLANT STARVATION from {sender} -> Temp rising!"
                            self.state["tampered_by"] = sender
                            
                        elif cmd == "RESET_NORMAL":
                            self.target_override["active"] = False
                            self.state["status"] = "NORMAL_OPERATING"
                            self.state["last_incident"] = f"Plant manually restored to safe baseline by {sender}"
                            self.state["tampered_by"] = "None"
                            
                except Exception as e:
                    pass
        except Exception as e:
            print(f"[!] Command listener error: {e}")
        finally:
            sock.close()

    def physics_loop(self):
        """Simulates physical plant dynamics with smooth realistic convergence."""
        while self.running:
            with self.lock:
                if self.target_override["active"]:
                    # Rapidly drift towards malicious injected targets
                    self.state["turbine_rpm"] += (self.target_override.get("turbine_rpm", 3000.0) - self.state["turbine_rpm"]) * 0.35
                    self.state["boiler_psi"] += (self.target_override.get("boiler_psi", 125.0) - self.state["boiler_psi"]) * 0.35
                    self.state["reactor_temp"] += (self.target_override.get("reactor_temp", 72.5) - self.state["reactor_temp"]) * 0.25
                    self.state["coolant_flow"] += (self.target_override.get("coolant_flow", 82.0) - self.state["coolant_flow"]) * 0.35
                else:
                    # Natural slight industrial fluctuation around baseline
                    self.state["turbine_rpm"] = 3000.0 + random.uniform(-15.0, 18.0)
                    self.state["boiler_psi"] = 125.0 + random.uniform(-1.5, 2.0)
                    self.state["reactor_temp"] = 72.5 + random.uniform(-0.4, 0.5)
                    self.state["coolant_flow"] = 82.0 + random.uniform(-1.0, 1.2)
                    self.state["grid_hz"] = 50.0 + random.uniform(-0.04, 0.04)
                    self.state["valve_open_pct"] = 85.0 + random.uniform(-0.5, 0.5)
                    
            time.sleep(0.5)

    def telemetry_broadcaster(self):
        """Broadcasts one-way UDP telemetry packets to Laptop B."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while self.running:
            with self.lock:
                telemetry = {
                    "source": "LAPTOP_A_SCADA_PLC",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                    "turbine_rpm": round(self.state["turbine_rpm"], 2),
                    "boiler_psi": round(self.state["boiler_psi"], 2),
                    "reactor_temp": round(self.state["reactor_temp"], 2),
                    "coolant_flow": round(self.state["coolant_flow"], 2),
                    "grid_hz": round(self.state["grid_hz"], 3),
                    "valve_open_pct": round(self.state["valve_open_pct"], 1),
                    "plant_status": self.state["status"],
                    "tampered_by": self.state["tampered_by"],
                    "seq_num": self.state["packets_sent"] + 1
                }
                self.state["packets_sent"] += 1
                
            try:
                data = json.dumps(telemetry).encode("utf-8")
                sock.sendto(data, (self.target_soc_ip, PORT_TELEMETRY_UDP))
            except Exception as e:
                pass
            time.sleep(1.0)
        sock.close()

    def print_status_screen(self):
        """Displays a clean real-time status monitor in the terminal."""
        while self.running:
            os.system('cls' if os.name == 'nt' else 'clear')
            with self.lock:
                rpm = self.state["turbine_rpm"]
                psi = self.state["boiler_psi"]
                temp = self.state["reactor_temp"]
                flow = self.state["coolant_flow"]
                status = self.state["status"]
                incident = self.state["last_incident"]
                target_ip = self.target_soc_ip
                pkts = self.state["packets_sent"]
            
            # Status badge
            if "NORMAL" in status:
                status_color = "[*] SECURE / NORMAL OPERATING"
            else:
                status_color = f"[!] {status} [PROCESS COMPROMISED!]"

            print(r"""
================================================================================
   LAPTOP A : INDUSTRIAL CONTROL SYSTEM (ICS/SCADA) & PLC SIMULATOR
   PROTECTED SIDE - ONE-WAY DATA DIODE EMITTER
================================================================================
""")
            print(f" Target SOC Receiver (Laptop B) : {target_ip}:{PORT_TELEMETRY_UDP}")
            print(f" Local Control Port (Laptop C)  : 0.0.0.0:{PORT_PLANT_CONTROL}")
            print(f" Telemetry Packets Broadcasted  : {pkts}")
            print(f" Current System Security Status : {status_color}")
            print("-" * 80)
            print(f" [1] Turbine Speed    : {rpm:7.1f} RPM   {'[CRITICAL OVER-SPEED]' if rpm > 4500 else '[NORMAL]'}")
            print(f" [2] Steam Boiler     : {psi:7.1f} PSI   {'[CRITICAL OVERPRESSURE]' if psi > 250 else '[NORMAL]'}")
            print(f" [3] Reactor Core     : {temp:7.1f} °C    {'[OVERHEATING HAZARD]' if temp > 100 else '[NORMAL]'}")
            print(f" [4] Coolant Valve    : {flow:7.1f} L/min {'[COOLANT STARVATION]' if flow < 30 else '[NORMAL]'}")
            print("-" * 80)
            print(f" Last Incident / Event : {incident}")
            print("=" * 80)
            print(" >> Emitting live telemetry to Laptop B every 1.0s...")
            print(" >> Press Ctrl+C in this terminal to stop.")
            time.sleep(1.0)


def main():
    print("=" * 70)
    print(" LAPTOP A - INDUSTRIAL PLANT / SCADA SIMULATOR STARTUP")
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
    
    # Start background threads
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
