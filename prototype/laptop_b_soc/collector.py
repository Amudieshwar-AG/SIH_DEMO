"""
LAPTOP B : UDP TELEMETRY & NETWORK FLOW COLLECTOR
SIH 2026 - System Hackers Prototype
"""

import socket
import json
import threading
import time
from collections import deque
from datetime import datetime

class SOCDataCollector:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(SOCDataCollector, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, telemetry_port=5005, traffic_port=5006, history_len=60):
        if self._initialized:
            return
        self.telemetry_port = telemetry_port
        self.traffic_port = traffic_port
        self.history_len = history_len
        self.running = True
        
        # In-memory storage buffers
        self.telemetry_history = deque(maxlen=history_len)
        self.packet_times = deque(maxlen=200)
        self.alert_history = deque(maxlen=100)
        
        # Latest cached status
        self.latest_telemetry = {
            "source": "WAITING_FOR_TELEMETRY",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "turbine_rpm": 3000.0,
            "boiler_psi": 125.0,
            "reactor_temp": 72.5,
            "coolant_flow": 82.0,
            "grid_hz": 50.0,
            "valve_open_pct": 85.0,
            "plant_status": "WAITING",
            "packets_received": 0,
            "packet_rate_pps": 1.0,
            "tampered_by": "None"
        }
        
        # Persistent Attack State (cannot be wiped by baseline telemetry)
        self.attack_lock = False
        self.active_attack_cmd = ""
        self.active_user = "LOCAL_OPERATOR"
        self.active_auth_status = "AUTHENTICATED_LOCAL"
        self.failed_login_count = 0
        self.tampered_by = "None"
        self.override_rpm = None
        self.override_psi = None
        self.override_temp = None
        self.override_flow = None
        self.override_status = None
        
        # Start background collection listeners
        self.start_listeners()
        self._initialized = True

    def start_listeners(self):
        t_tel = threading.Thread(target=self._telemetry_listener, daemon=True)
        t_traf = threading.Thread(target=self._traffic_listener, daemon=True)
        t_rate = threading.Thread(target=self._rate_calculator, daemon=True)
        t_tel.start()
        t_traf.start()
        t_rate.start()

    def _telemetry_listener(self):
        """Receives one-way telemetry from Laptop A (Port 5005) + direct attack injections from Laptop C."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("0.0.0.0", self.telemetry_port))
            while self.running:
                data, addr = sock.recvfrom(4096)
                now = time.time()
                self.packet_times.append(now)
                
                try:
                    payload = json.loads(data.decode("utf-8"))
                    sender_ip = addr[0]
                    req_type = payload.get("type", "")
                    cmd = payload.get("command", "")
                    
                    with self._lock:
                        # 1. Handle Attack Injections from Laptop C
                        if req_type == "LOGIN_ATTEMPT":
                            self.failed_login_count += 1
                            self.active_auth_status = "FAILED_AUTH_ATTEMPT"
                            self.tampered_by = sender_ip
                            self.add_alert(
                                event_type="CREDENTIAL_STUFFING_BRUTEFORCE_ATTACK",
                                severity="HIGH",
                                source_ip=sender_ip,
                                details=f"Failed login attempt #{self.failed_login_count} detected from {sender_ip}"
                            )
                            
                        elif req_type == "MALICIOUS_OVERRIDE" or cmd in ["OVERRIDE_TURBINE_RPM", "OVERPRESSURE_BOILER", "CHOKE_COOLANT"]:
                            self.attack_lock = True
                            user = payload.get("username", "admin_plc")
                            self.active_user = user
                            self.active_auth_status = "COMPROMISED_CREDENTIAL_LOGIN"
                            self.tampered_by = sender_ip
                            
                            if cmd == "OVERRIDE_TURBINE_RPM":
                                self.override_rpm = float(payload.get("target_rpm", 5850.0))
                                self.override_status = "CRITICAL_TURBINE_OVERSPEED"
                            elif cmd == "OVERPRESSURE_BOILER":
                                self.override_psi = float(payload.get("target_psi", 420.0))
                                self.override_status = "CRITICAL_BOILER_OVERPRESSURE"
                            elif cmd == "CHOKE_COOLANT":
                                self.override_flow = 4.0
                                self.override_temp = 125.0
                                self.override_status = "THERMAL_RUNAWAY_ALERT"
                                
                        elif req_type in ["RESET_NORMAL", "SERVER_POWER_ON"] or cmd in ["RESET_NORMAL", "SERVER_POWER_ON"]:
                            self.attack_lock = False
                            self.active_user = "LOCAL_OPERATOR"
                            self.active_auth_status = "AUTHENTICATED_LOCAL"
                            self.failed_login_count = 0
                            self.tampered_by = "None"
                            self.override_rpm = None
                            self.override_psi = None
                            self.override_temp = None
                            self.override_flow = None
                            self.override_status = None

                        # 2. Ingest plant physical readings
                        if "turbine_rpm" in payload and req_type not in ["MALICIOUS_OVERRIDE", "LOGIN_ATTEMPT"]:
                            payload["sender_ip"] = sender_ip
                            payload["recv_time"] = datetime.now().strftime("%H:%M:%S")
                            self.latest_telemetry.update(payload)
                            self.latest_telemetry["packets_received"] = self.latest_telemetry.get("packets_received", 0) + 1
                            
                        # 3. Apply persistent attack overlays if attack active
                        if self.failed_login_count > 0:
                            self.latest_telemetry["failed_login_count"] = self.failed_login_count
                            if not self.attack_lock:
                                self.latest_telemetry["auth_status"] = self.active_auth_status
                                self.latest_telemetry["tampered_by"] = self.tampered_by
                                
                        if self.attack_lock:
                            self.latest_telemetry["active_user"] = self.active_user
                            self.latest_telemetry["auth_status"] = self.active_auth_status
                            self.latest_telemetry["tampered_by"] = self.tampered_by
                            if self.override_rpm is not None:
                                self.latest_telemetry["turbine_rpm"] = self.override_rpm
                            if self.override_psi is not None:
                                self.latest_telemetry["boiler_psi"] = self.override_psi
                            if self.override_temp is not None:
                                self.latest_telemetry["reactor_temp"] = self.override_temp
                            if self.override_flow is not None:
                                self.latest_telemetry["coolant_flow"] = self.override_flow
                            if self.override_status is not None:
                                self.latest_telemetry["plant_status"] = self.override_status
                                
                        self.telemetry_history.append(dict(self.latest_telemetry))
                except Exception:
                    pass
        except Exception as e:
            print(f"[!] Telemetry listener error: {e}")
        finally:
            sock.close()

    def _traffic_listener(self):
        """Receives test traffic / floods from Laptop C (Port 5006)."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("0.0.0.0", self.traffic_port))
            while self.running:
                data, addr = sock.recvfrom(4096)
                now = time.time()
                self.packet_times.append(now)
                
                # Check for attack signatures in test traffic
                try:
                    payload = json.loads(data.decode("utf-8"))
                    attack_type = payload.get("attack_type", "TEST_TRAFFIC")
                    self.add_alert(
                        event_type=f"DIRECT_ATTACK_{attack_type}",
                        severity="HIGH",
                        source_ip=addr[0],
                        details=f"Injected payload: {payload.get('description', 'High rate flow')}"
                    )
                except Exception:
                    pass
        except Exception as e:
            pass
        finally:
            sock.close()

    def _rate_calculator(self):
        """Computes instantaneous packets per second (PPS)."""
        while self.running:
            now = time.time()
            # Count packets in the last 1.0 second
            recent = [t for t in self.packet_times if now - t <= 1.0]
            with self._lock:
                self.latest_telemetry["packet_rate_pps"] = len(recent)
            time.sleep(0.5)

    def add_alert(self, event_type, severity, source_ip, details):
        with self._lock:
            alert = {
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "event_type": event_type,
                "severity": severity,
                "source_ip": source_ip,
                "details": details
            }
            self.alert_history.appendleft(alert)

    def get_latest(self):
        with self._lock:
            return dict(self.latest_telemetry)

    def get_history(self):
        with self._lock:
            return list(self.telemetry_history)

    def get_alerts(self):
        with self._lock:
            return list(self.alert_history)

    def trigger_isolation(self):
        with self._lock:
            self.isolation_mode = True
            self.add_alert(
                event_type="DEFENSIVE_COUNTERMEASURE_ACTIVATED",
                severity="INFO",
                source_ip="LOCAL_SOC",
                details="Data-Diode Air-Gap interlock engaged. Inbound control isolated."
            )

    def reset_isolation(self):
        with self._lock:
            self.isolation_mode = False
