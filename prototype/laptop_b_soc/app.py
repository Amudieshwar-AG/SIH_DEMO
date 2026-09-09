"""
=============================================================================
 LAPTOP B : AI/ML SOC DEFENSE & THREAT CLASSIFICATION COMMAND CENTER
 SIH 2026 - System Hackers Prototype
=============================================================================
Run with: python -m streamlit run app.py --server.port 8502
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(__file__))
from collector import SOCDataCollector
from detector import ICSAnomalyDetector

st.set_page_config(
    page_title="SIH 2026 | ICS Cyber Defense & Threat AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def get_soc_collector():
    return SOCDataCollector()

@st.cache_resource
def get_ics_detector():
    return ICSAnomalyDetector()

collector = get_soc_collector()
detector = get_ics_detector()

st.markdown("""
<style>
    .stApp {
        background-color: #080d1a;
        color: #e2e8f0;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    .soc-banner-safe {
        background: linear-gradient(90deg, #064e3b 0%, #047857 50%, #065f46 100%);
        border: 1px solid #10b981;
        box-shadow: 0 0 20px rgba(16, 185, 129, 0.3);
        border-radius: 12px;
        padding: 16px 24px;
        margin-bottom: 20px;
    }
    .soc-banner-danger {
        background: linear-gradient(90deg, #7f1d1d 0%, #b91c1c 50%, #991b1b 100%);
        border: 2px solid #ef4444;
        box-shadow: 0 0 30px rgba(239, 68, 68, 0.6);
        border-radius: 12px;
        padding: 16px 24px;
        margin-bottom: 20px;
        animation: pulse-danger 1.5s infinite alternate;
    }
    @keyframes pulse-danger {
        from { box-shadow: 0 0 15px rgba(239, 68, 68, 0.4); }
        to { box-shadow: 0 0 35px rgba(239, 68, 68, 0.8); }
    }
    .soc-card {
        background: #111c33;
        border: 1px solid #1e293b;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .soc-card-header {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #94a3b8;
        margin-bottom: 6px;
    }
    .soc-metric-val {
        font-size: 1.7rem;
        font-weight: 700;
        color: #f8fafc;
    }
    .threat-intel-box {
        background: #151e36;
        border-left: 5px solid #38bdf8;
        padding: 15px 20px;
        border-radius: 6px;
    }
    .threat-intel-danger {
        background: #2a1215;
        border-left: 5px solid #ef4444;
        padding: 15px 20px;
        border-radius: 6px;
    }
</style>
""", unsafe_allow_html=True)

telemetry = collector.get_latest()
analysis = detector.analyze(telemetry)
history = collector.get_history()
alerts = collector.get_alerts()

# Auto-log alert on detection
if analysis["is_anomaly"] and analysis["severity"] in ["HIGH", "CRITICAL"]:
    if not alerts or alerts[0].get("event_type") != analysis["threat_name"]:
        collector.add_alert(
            event_type=analysis["threat_name"],
            severity=analysis["severity"],
            source_ip=telemetry.get("tampered_by", telemetry.get("sender_ip", "127.0.0.1")),
            details=analysis["root_cause"]
        )

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shield.png", width=64)
    st.title("🛡️ SOC Threat Intel Hub")
    st.caption("SIH 2026 | Team System Hackers")
    st.markdown("---")
    
    st.subheader("🔑 Authentication Monitor")
    st.write(f"• **Active Session:** `{analysis['active_user']}`")
    st.write(f"• **Session State:** `{analysis['auth_status']}`")
    st.write(f"• **Failed Login Surge:** `{analysis['failed_logins']}` attempts")
    st.write(f"• **Attacker IP:** `{analysis['tampered_by']}`")
    
    st.markdown("---")
    st.subheader("⚡ Automated Defense Actions")
    if not collector.isolation_mode:
        if st.button("🚨 TRIGGER DATA-DIODE ISOLATION", use_container_width=True, type="primary"):
            collector.trigger_isolation()
            st.rerun()
    else:
        st.error("🛡️ AIR-GAP ISOLATION ENGAGED")
        if st.button("🔄 RESTORE NORMAL LINK", use_container_width=True):
            collector.reset_isolation()
            st.rerun()

    st.markdown("---")
    auto_refresh = st.checkbox("🔄 Live Real-Time Auto-Refresh (1.5s)", value=True)
    st.write(f"• **Packets Received:** `{telemetry.get('packets_received', 0)}`")
    st.write(f"• **Flow Ingestion Rate:** `{telemetry.get('packet_rate_pps', 1)} pkts/s`")

# 1. Main Banner
if not analysis["is_anomaly"]:
    st.markdown(f"""
    <div class="soc-banner-safe">
        <h2 style="margin:0; color:#10b981; font-size:1.4rem;">🟢 DEFCON 5 : INDUSTRIAL PROCESS & ACCESS SECURE</h2>
        <p style="margin:4px 0 0 0; color:#d1fae5; font-size:0.9rem;">
            One-Way Telemetry Verified. Authorized User: <b>{analysis['active_user']}</b> | AI Anomaly Score: <b>{analysis['anomaly_score']}%</b>
        </p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="soc-banner-danger">
        <h2 style="margin:0; color:#ffffff; font-size:1.4rem;">🚨 THREAT ALERT: {analysis['threat_name']}</h2>
        <p style="margin:4px 0 0 0; color:#fecaca; font-size:0.9rem;">
            <b>AI Anomaly Confidence: {analysis['anomaly_score']}%</b> | {analysis['mitre_id']}
        </p>
    </div>
    """, unsafe_allow_html=True)

# 2. Key Metrics Row
col1, col2, col3, col4 = st.columns(4)

with col1:
    user_st = analysis["active_user"]
    u_color = "#ef4444" if user_st != "LOCAL_OPERATOR" and user_st != "None" else "#10b981"
    st.markdown(f"""
    <div class="soc-card">
        <div class="soc-card-header">PLC Authenticated User</div>
        <div class="soc-metric-val" style="color:{u_color};">{user_st}</div>
        <div style="font-size:0.8rem; color:#64748b; margin-top:4px;">Failed Attempts: {analysis['failed_logins']}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    rpm = telemetry.get("turbine_rpm", 3000.0)
    r_color = "#ef4444" if rpm > 4500 else "#38bdf8"
    st.markdown(f"""
    <div class="soc-card">
        <div class="soc-card-header">Turbine Speed</div>
        <div class="soc-metric-val" style="color:{r_color};">{rpm:.1f} <span style="font-size:1rem;color:#94a3b8;">RPM</span></div>
        <div style="font-size:0.8rem; color:#64748b; margin-top:4px;">Nominal: 3000 RPM</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    psi = telemetry.get("boiler_psi", 125.0)
    p_color = "#ef4444" if psi > 250 else "#38bdf8"
    st.markdown(f"""
    <div class="soc-card">
        <div class="soc-card-header">Steam Boiler Pressure</div>
        <div class="soc-metric-val" style="color:{p_color};">{psi:.1f} <span style="font-size:1rem;color:#94a3b8;">PSI</span></div>
        <div style="font-size:0.8rem; color:#64748b; margin-top:4px;">Nominal: 125 PSI</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    temp = telemetry.get("reactor_temp", 72.5)
    t_color = "#ef4444" if temp > 95.0 else "#38bdf8"
    st.markdown(f"""
    <div class="soc-card">
        <div class="soc-card-header">Reactor Temperature</div>
        <div class="soc-metric-val" style="color:{t_color};">{temp:.1f} <span style="font-size:1rem;color:#94a3b8;">°C</span></div>
        <div style="font-size:0.8rem; color:#64748b; margin-top:4px;">Nominal: 72.5 °C</div>
    </div>
    """, unsafe_allow_html=True)

# 3. Chart & Threat Intel Row
chart_col, intel_col = st.columns([2, 1])

with chart_col:
    st.subheader("📈 Live Physical Telemetry Stream")
    if len(history) > 1:
        df = pd.DataFrame(history)
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=df["turbine_rpm"], mode='lines+markers', name='Turbine RPM', line=dict(color='#38bdf8', width=2.5), yaxis='y1'))
        fig.add_trace(go.Scatter(y=df["boiler_psi"], mode='lines', name='Boiler PSI', line=dict(color='#f59e0b', width=2, dash='dot'), yaxis='y2'))
        fig.update_layout(
            paper_bgcolor='#0b111e', plot_bgcolor='#111c33', font=dict(color='#94a3b8'),
            margin=dict(l=20, r=20, t=30, b=20), height=300,
            xaxis=dict(showgrid=True, gridcolor='#1e293b', title_text="Time Slices"),
            yaxis=dict(title_text="Turbine Speed (RPM)", title_font=dict(color="#38bdf8"), tickfont=dict(color="#38bdf8"), showgrid=True, gridcolor='#1e293b'),
            yaxis2=dict(title_text="Boiler Pressure (PSI)", title_font=dict(color="#f59e0b"), tickfont=dict(color="#f59e0b"), overlaying='y', side='right'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Awaiting telemetry stream from Laptop A...")

with intel_col:
    st.subheader("🧠 AI Threat Classifier & MITRE")
    box_class = "threat-intel-danger" if analysis["is_anomaly"] else "threat-intel-box"
    st.markdown(f"""
    <div class="{box_class}">
        <div style="font-size:0.8rem; color:#94a3b8; font-weight:600;">AI THREAT SIGNATURE</div>
        <div style="font-size:1.1rem; font-weight:bold; color:#f8fafc; margin:4px 0;">{analysis['threat_name']}</div>
        <div style="font-size:0.85rem; color:#cbd5e1; margin-top:8px;">
            <b>• Severity:</b> <span style="color:{'#ef4444' if analysis['severity']=='CRITICAL' else '#10b981'};">{analysis['severity']}</span><br>
            <b>• MITRE Mapping:</b> {analysis['mitre_id']}<br>
            <b>• AI Anomaly Probability:</b> {analysis['anomaly_score']}%<br>
            <b>• Forensic Root Cause:</b> {analysis['root_cause']}
        </div>
    </div>
    """, unsafe_allow_html=True)

# 4. Audit Log Table
st.markdown("---")
st.subheader("📋 Security Incident & Authentication Audit Log")
if alerts:
    alert_df = pd.DataFrame(alerts)
    st.dataframe(alert_df, use_container_width=True, hide_index=True)
else:
    st.success("No security violations detected. Operating securely.")

# Auto-refresh loop triggered after full page render
if auto_refresh:
    time.sleep(1.5)
    st.rerun()

