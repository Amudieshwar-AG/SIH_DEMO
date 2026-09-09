"""
LAPTOP B : ML ANOMALY DETECTION & THREAT CLASSIFICATION ENGINE
SIH 2026 - System Hackers Prototype
"""

import numpy as np
from sklearn.ensemble import IsolationForest

class ICSAnomalyDetector:
    def __init__(self):
        # Baseline normal ranges
        self.baselines = {
            "turbine_rpm": (2900, 3200),
            "boiler_psi": (115, 140),
            "reactor_temp": (68.0, 78.0),
            "coolant_flow": (75.0, 90.0),
            "grid_hz": (49.8, 50.2),
            "packet_rate_pps": (0, 5)
        }
        
        # Pre-train an Isolation Forest on synthetic normal ICS operational baseline
        self.model = IsolationForest(contamination=0.05, random_state=42)
        self._fit_baseline_model()

    def _fit_baseline_model(self):
        """Generates synthetic normal baseline operating distribution to fit ML model."""
        np.random.seed(42)
        n_samples = 300
        
        rpm = np.random.normal(3000, 30, n_samples)
        psi = np.random.normal(125, 3, n_samples)
        temp = np.random.normal(72.5, 1.2, n_samples)
        flow = np.random.normal(82, 2.5, n_samples)
        hz = np.random.normal(50.0, 0.05, n_samples)
        pps = np.random.poisson(1.5, n_samples)
        
        X_train = np.column_stack([rpm, psi, temp, flow, hz, pps])
        self.model.fit(X_train)

    def analyze(self, telemetry):
        """
        Analyzes a single telemetry record using ML Isolation Forest + Threat Signature Engine.
        Returns:
            - is_anomaly (bool)
            - anomaly_score (float 0.0 - 100.0%)
            - threat_name (str)
            - severity (str: NORMAL, MEDIUM, CRITICAL)
            - mitre_id (str)
            - root_cause (str)
        """
        rpm = telemetry.get("turbine_rpm", 3000.0)
        psi = telemetry.get("boiler_psi", 125.0)
        temp = telemetry.get("reactor_temp", 72.5)
        flow = telemetry.get("coolant_flow", 82.0)
        hz = telemetry.get("grid_hz", 50.0)
        pps = telemetry.get("packet_rate_pps", 1.0)
        tampered_by = telemetry.get("tampered_by", "None")
        
        # 1. ML Isolation Forest Anomaly Score
        sample = np.array([[rpm, psi, temp, flow, hz, pps]])
        raw_score = self.model.decision_function(sample)[0]  # Lower = more abnormal
        # Map raw score (-0.5 to +0.2) to percentage (0% = Normal, 100% = Extreme Anomaly)
        ml_anomaly_pct = max(0.0, min(100.0, round((0.2 - raw_score) * 150, 1)))
        
        # 2. Heuristic & MITRE ATT&CK Threat Classifier
        threat_name = "NORMAL_PROCESS_EQUILIBRIUM"
        severity = "NORMAL"
        mitre_id = "N/A"
        root_cause = "All industrial parameters within nominal safe thresholds."
        is_anomaly = False

        if rpm > 4500:
            is_anomaly = True
            severity = "CRITICAL"
            threat_name = "STUXNET_TURBINE_OVERSPEED_ATTACK"
            mitre_id = "MITRE T0836 (Modify Parameter) & T0846 (Impair Process Control)"
            root_cause = f"Turbine RPM ({rpm:.1f}) exceeded centrifugal mechanical safety threshold (4500 RPM)."
            ml_anomaly_pct = max(ml_anomaly_pct, 98.6)
            
        elif psi > 250:
            is_anomaly = True
            severity = "CRITICAL"
            threat_name = "BOILER_CATASTROPHIC_OVERPRESSURE"
            mitre_id = "MITRE T0855 (Unauthorized Command) & T0828 (Loss of Safety)"
            root_cause = f"Boiler Steam Pressure ({psi:.1f} PSI) exceeded burst disc safety threshold (250 PSI)."
            ml_anomaly_pct = max(ml_anomaly_pct, 97.8)
            
        elif flow < 30.0 or temp > 95.0:
            is_anomaly = True
            severity = "HIGH"
            threat_name = "COOLANT_STARVATION_THERMAL_RUNAWAY"
            mitre_id = "MITRE T0806 (Brute Force I/O Manipulation)"
            root_cause = f"Coolant flow choked to {flow:.1f} L/min resulting in core thermal spike to {temp:.1f} °C."
            ml_anomaly_pct = max(ml_anomaly_pct, 94.2)
            
        elif pps > 30:
            is_anomaly = True
            severity = "HIGH"
            threat_name = "VOLUMETRIC_TELEMETRY_FLOOD_DDOS"
            mitre_id = "MITRE T0814 (Denial of Service - Sensor Jamming)"
            root_cause = f"Abnormal inbound traffic surge ({pps} pkts/sec) attempting to saturate SOC collector."
            ml_anomaly_pct = max(ml_anomaly_pct, 92.5)
            
        elif ml_anomaly_pct > 65.0:
            is_anomaly = True
            severity = "MEDIUM"
            threat_name = "STATISTICAL_PROCESS_DRIFT_ANOMALY"
            mitre_id = "MITRE T0849 (Sensing Parameter Spoofing)"
            root_cause = "Unusual correlation between grid frequency and pressure detected by ML Isolation Forest."

        return {
            "is_anomaly": is_anomaly,
            "anomaly_score": ml_anomaly_pct,
            "threat_name": threat_name,
            "severity": severity,
            "mitre_id": mitre_id,
            "root_cause": root_cause,
            "tampered_by": tampered_by
        }
