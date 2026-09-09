"""
=============================================================================
 LAPTOP C : CYBER-WEAPON & THREAT INJECTION WEB CONSOLE (STREAMLIT)
 SIH 2026 - System Hackers Prototype
=============================================================================
Run with: streamlit run attacker_ui.py --server.port 8503
"""

import streamlit as st
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

st.set_page_config(
    page_title="Threat & Attack Injector (Laptop C)",
    page_icon="⚡",
    layout="wide"
)

# Dark Red / Cyber-Attacker Theme
st.markdown("""
<style>
    .stApp { background-color: #0d0a14; color: #f3e8ff; font-family: 'Inter', sans-serif; }
    .attack-card {
        background: #1e132b;
        border: 1px solid #4c1d95;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .attack-card:hover {
        border-color: #a855f7;
    }
    .header-box {
        background: linear-gradient(90deg, #581c87 0%, #3b0764 100%);
        border: 1px solid #9333ea;
        padding: 16px 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-box">
    <h2 style="margin:0; color:#f3e8ff;">⚡ Laptop C : Threat & Traffic Simulator Console</h2>
    <p style="margin:4px 0 0 0; color:#d8b4fe; font-size:0.9rem;">
        Adversary Simulation Suite for SIH 2026 Live Defense Validation
    </p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.subheader("🎯 Target Configurations")
    target_a_ip = st.text_input("Laptop A (Plant) IP:", value=DEFAULT_LAPTOP_A_IP)
    target_b_ip = st.text_input("Laptop B (SOC) IP:", value=DEFAULT_LAPTOP_B_IP)
    st.markdown("---")
    st.caption("All control packets transmitted over UDP sockets.")

def send_cmd(cmd_dict):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        data = json.dumps(cmd_dict).encode("utf-8")
        sock.sendto(data, (target_a_ip, PORT_PLANT_CONTROL))
        st.toast(f"✅ Injected command to {target_a_ip}:{PORT_PLANT_CONTROL}", icon="🚀")
    except Exception as e:
        st.error(f"Failed to send: {e}")
    finally:
        sock.close()

def send_flood():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    payload = json.dumps({"attack_type": "VOLUMETRIC_FLOOD", "description": "High-rate UDP sensor flood"}).encode("utf-8")
    for _ in range(200):
        try:
            sock.sendto(payload, (target_b_ip, PORT_TRAFFIC_TEST))
            time.sleep(0.01)
        except Exception:
            pass
    sock.close()
    st.toast(f"✅ 200 Flooding packets fired at {target_b_ip}:{PORT_TRAFFIC_TEST}", icon="🌊")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🏭 Physical SCADA Attack Vectors (Targets Laptop A)")
    
    with st.container():
        st.markdown("""
        <div class="attack-card">
            <h4 style="margin:0; color:#e9d5ff;">🚨 1. Stuxnet Turbine Over-speed</h4>
            <p style="font-size:0.85rem; color:#c084fc; margin:4px 0 10px 0;">
                Modifies PLC setpoint registers to force turbine beyond 5,800 RPM.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("EXECUTE TURBINE OVERSPEED ATTACK", type="primary", use_container_width=True):
            send_cmd({"command": "OVERRIDE_TURBINE_RPM", "target_rpm": 5850.0})
            st.success("Target setpoint updated to 5,850 RPM!")

    with st.container():
        st.markdown("""
        <div class="attack-card">
            <h4 style="margin:0; color:#e9d5ff;">🚨 2. Boiler Catastrophic Overpressure</h4>
            <p style="font-size:0.85rem; color:#c084fc; margin:4px 0 10px 0;">
                Closes relief valves and spikes pressure to 420 PSI (Burst Hazard).
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("EXECUTE BOILER OVERPRESSURE ATTACK", type="primary", use_container_width=True):
            send_cmd({"command": "OVERPRESSURE_BOILER", "target_psi": 420.0})
            st.success("Target setpoint updated to 420 PSI!")

    with st.container():
        st.markdown("""
        <div class="attack-card">
            <h4 style="margin:0; color:#e9d5ff;">🚨 3. Coolant Starvation / Thermal Runaway</h4>
            <p style="font-size:0.85rem; color:#c084fc; margin:4px 0 10px 0;">
                Chokes reactor coolant circulation pump to induce thermal meltdown.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("EXECUTE COOLANT CHOKE ATTACK", type="primary", use_container_width=True):
            send_cmd({"command": "CHOKE_COOLANT"})
            st.success("Coolant pump choked!")

with col2:
    st.markdown("### 🌐 Network & Volumetric Attacks (Targets Laptop B)")
    
    with st.container():
        st.markdown("""
        <div class="attack-card">
            <h4 style="margin:0; color:#e9d5ff;">🌊 4. Volumetric UDP Sensor Flooding (DDoS)</h4>
            <p style="font-size:0.85rem; color:#c084fc; margin:4px 0 10px 0;">
                Jams the SOC telemetry receiver with 200+ packets/sec burst.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("LAUNCH HIGH-RATE SENSOR FLOOD", use_container_width=True):
            send_flood()

    st.markdown("### 🔄 Baseline Management")
    with st.container():
        st.markdown("""
        <div class="attack-card" style="background:#0f172a; border-color:#334155;">
            <h4 style="margin:0; color:#38bdf8;">🟢 Restore Plant to Safe Equilibrium</h4>
            <p style="font-size:0.85rem; color:#94a3b8; margin:4px 0 10px 0;">
                Resets all parameters on Laptop A back to safe baseline.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("RESTORE SAFE BASELINE", use_container_width=True):
            send_cmd({"command": "RESET_NORMAL"})
            st.info("Reset command broadcasted to plant.")
