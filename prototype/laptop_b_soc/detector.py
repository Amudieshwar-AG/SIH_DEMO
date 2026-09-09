"""
LAPTOP B : AI/ML ANOMALY DETECTOR & CREDENTIAL THREAT CLASSIFIER
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
            "grid_hz": (49.8, 50.2)
        }
        
        # Pre-train Isolation Forest on normal physical baseline
        self.model = IsolationForest(contamination=0.05, random_state=42)
        self._fit_baseline_model()

    def _fit_baseline_model(self):
        """Fits ML baseline model on normal operating distributions."""
        np.random.seed(42)
        n_samples = 300
        
        rpm = np.random.normal(3000, 30, n_samples)
        psi = np.random.normal(125, 3, n_samples)
        temp = np.random.normal(72.5, 1.2, n_samples)
        flow = np.random.normal(82, 2.5, n_samples)
        hz = np.random.normal(50.0, 0.05, n_samples)
        
        X_train = np.column_stack([rpm, psi, temp, flow, hz])
        self.model.fit(X_train)

    def analyze(self, telemetry):
        """
        Dual AI Engine:
        1. ML Isolation Forest: Physical process anomaly scoring.
        2. Threat & Credential Classifier: Analyzes authentication security & MITRE techniques.
        """
        rpm = telemetry.get("turbine_rpm", 3000.0)
        psi = telemetry.get("boiler_psi", 125.0)
        temp = telemetry.get("reactor_temp", 72.5)
        flow = telemetry.get("coolant_flow", 82.0)
        hz = telemetry.get("grid_hz", 50.0)
        
        # Security telemetry fields
        active_user = telemetry.get("active_user", "LOCAL_OPERATOR")
        auth_status = telemetry.get("auth_status", "AUTHENTICATED_LOCAL")
        failed_logins = telemetry.get("failed_login_count", 0)
        tampered_by = telemetry.get("tampered_by", "None")
        
        # 1. Compute ML Isolation Forest Anomaly Score
        sample = np.array([[rpm, psi, temp, flow, hz]])
        raw_score = self.model.decision_function(sample)[0]
        ml_score = max(0.0, min(100.0, round((0.2 - raw_score) * 150, 1)))

        # 2. Threat & Credential Security Classification
        threat_name = "SECURE_BASELINE_OPERATIONS"
        severity = "NORMAL"
        mitre_id = "N/A"
        root_cause = "All industrial parameters & user sessions within nominal authorized baseline."
        is_anomaly = False

        # Threat Rules & AI Correlation
        if failed_logins >= 3 or auth_status == "FAILED_AUTH_ATTEMPT":
            is_anomaly = True
            severity = "HIGH"
            threat_name = "CREDENTIAL_STUFFING_BRUTEFORCE_ATTACK"
            mitre_id = "MITRE T0812 (Default/Stolen Credentials) & T0806 (Brute Force Access)"
            root_cause = f"High-frequency failed authentication attempts ({failed_logins} failures) detected on PLC gateway."
            ml_score = max(ml_score, 88.5)

        elif auth_status in ["COMPROMISED_CREDENTIAL_LOGIN", "PRIVILEGED_COMMAND_EXECUTED"]:
            is_anomaly = True
            severity = "CRITICAL"
            if rpm > 4500:
                threat_name = "STOLEN_CREDENTIAL_TURBINE_OVERSPEED"
                mitre_id = "MITRE T0859 (Valid Accounts Abuse) & T0836 (Modify Parameter)"
                root_cause = f"Attacker ({tampered_by}) hijacked '{active_user}' credentials to force Turbine speed to {rpm:.1f} RPM."
                ml_score = 99.2
            elif psi > 250:
                threat_name = "STOLEN_CREDENTIAL_BOILER_OVERPRESSURE"
                mitre_id = "MITRE T0859 (Valid Accounts Abuse) & T0846 (Impair Process Control)"
                root_cause = f"Attacker ({tampered_by}) used stolen PLC credentials to spike Boiler pressure to {psi:.1f} PSI."
                ml_score = 98.7
            elif flow < 30.0:
                threat_name = "STOLEN_CREDENTIAL_COOLANT_STARVATION"
                mitre_id = "MITRE T0859 (Valid Accounts) & T0828 (Loss of Safety)"
                root_cause = f"Attacker ({tampered_by}) authenticated as '{active_user}' and choked reactor coolant pump."
                ml_score = 97.5
            else:
                threat_name = "UNAUTHORIZED_PRIVILEGED_LOGIN_DETECTED"
                mitre_id = "MITRE T0859 (Valid Accounts - Stolen Credential)"
                root_cause = f"Unauthorized remote session authenticated as '{active_user}' from IP {tampered_by}."
                ml_score = 85.0

        elif rpm > 4500 or psi > 250 or flow < 30.0 or ml_score > 70.0:
            is_anomaly = True
            severity = "HIGH"
            threat_name = "PHYSICAL_PROCESS_DEVIATION"
            mitre_id = "MITRE T0836 (Modify Parameter)"
            root_cause = "Sensor telemetry deviated significantly from trained ML baseline equilibrium."
            ml_score = max(ml_score, 92.0)

        return {
            "is_anomaly": is_anomaly,
            "anomaly_score": ml_score,
            "threat_name": threat_name,
            "severity": severity,
            "mitre_id": mitre_id,
            "root_cause": root_cause,
            "active_user": active_user,
            "auth_status": auth_status,
            "failed_logins": failed_logins,
            "tampered_by": tampered_by
        }
