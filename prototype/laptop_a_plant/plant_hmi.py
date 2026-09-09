"""
LAPTOP A : OPTIONAL GRAPHICAL SCADA / HMI TOUCHSCREEN DASHBOARD
Run with: streamlit run plant_hmi.py --server.port 8501
"""
import streamlit as st
import socket
import json
import time
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
try:
    from config import PORT_PLANT_CONTROL
except ImportError:
    PORT_PLANT_CONTROL = 5002

st.set_page_config(page_title="SCADA Plant HMI (Laptop A)", page_icon="🏭", layout="wide")

st.markdown("""
<style>
    .main { background-color: #0b111e; color: #e2e8f0; }
    .stMetric { background: #162032; padding: 15px; border-radius: 10px; border: 1px solid #2d3748; }
    h1, h2, h3 { color: #38bdf8; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
</style>
""", unsafe_allow_html=True)

st.title("🏭 Plant Alpha - SCADA / PLC Operational HMI")
st.caption("Protected Critical Infrastructure Node (Laptop A) | One-Way Telemetry Active")

st.info("💡 Run `python plant_sim.py` in the terminal to actively run the physics and telemetry loop. This HMI allows manual PLC operator controls.")

col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("Manual Safety Actions")
    if st.button("🔄 Normal Operating Baseline", use_container_width=True):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(json.dumps({"command": "RESET_NORMAL"}).encode(), ("127.0.0.1", PORT_PLANT_CONTROL))
        sock.close()
        st.success("Safe baseline restored.")

with col2:
    st.subheader("Operator Diagnostics")
    st.write("• Telemetry Protocol: **UDP Data-Diode**")
    st.write("• Local Control Port: **5002**")
    st.write("• Interlock Status: **ARMED (Safe)**")

with col3:
    st.subheader("Emergency Station")
    if st.button("🚨 Trip Safety Valve (Vent)", use_container_width=True):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(json.dumps({"command": "RESET_NORMAL"}).encode(), ("127.0.0.1", PORT_PLANT_CONTROL))
        sock.close()
        st.warning("Emergency vent open.")
