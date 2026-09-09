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
        
        # Active mitigation flag
        self.isolation_mode = False
        
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
        """Receives one-way telemetry from Laptop A (Port 5005)."""
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
                    payload["sender_ip"] = addr[0]
                    payload["recv_time"] = datetime.now().strftime("%H:%M:%S")
                    
                    with self._lock:
                        self.latest_telemetry.update(payload)
                        self.latest_telemetry["packets_received"] = self.latest_telemetry.get("packets_received", 0) + 1
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
