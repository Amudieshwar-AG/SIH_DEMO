"""
=============================================================================
 LAPTOP B : MONITORING SIDE - AI/ML SOC DEFENSE & THREAT INTEL COMMAND CENTER
 SIH 2026 - System Hackers Prototype
=============================================================================
Run with: streamlit run app.py --server.port 8502
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import time
from datetime import datetime
import sys
import os

# Ensure local imports work cleanly
sys.path.append(os.path.dirname(__file__))
from collector import SOCDataCollector
from detector import ICSAnomalyDetector

# Configure Streamlit Page
st.set_page_config(
    page_title="SIH 2026 | ICS Cyber-Physical SOC Hub",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Collector & Detector Singletons
collector = SOCDataCollector()
detector = ICSAnomalyDetector()

# Dark Cyber SOC CSS Styling
st.markdown("""
<style>
    /* Dark Theme Cyberpunk SOC Styling */
    .stApp {
        background-color: #080d1a;
        color: #e2e8f0;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    /* Top Banner Styles */
    .soc-banner-safe {
        background: linear-gradient(90deg, #064e3b 0%, #047857 50%, #065f46 100%);
        border: 1px solid #10b981;
        box-shadow: 0 0 20px rgba(16, 185, 129, 0.3);
        border-radius: 12px;
        padding: 16px 24px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
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
    
    /* Card Container */
    .soc-card {
        background: #111c33;
        border: 1px solid #1e293b;
        border-radius: 10px;
        padding: 18px;
        margin-bottom: 15px;
    }
    .soc-card-header {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #94a3b8;
        margin-bottom: 8px;
    }
    .soc-metric-val {
        font-size: 1.8rem;
        font-weight: 700;
        color: #f8fafc;
    }
    
    /* Threat Intelligence Box */
    .threat-intel-box {
        background: #151e36;
        border-left: 5px solid #38bdf8;
        padding: 15px 20px;
        border-radius: 6px;
        margin-top: 10px;
    }
    .threat-intel-danger {
        background: #2a1215;
        border-left: 5px solid #ef4444;
        padding: 15px 20px;
        border-radius: 6px;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Fetch latest data and run analysis
telemetry = collector.get_latest()
analysis = detector.analyze(telemetry)
history = collector.get_history()
alerts = collector.get_alerts()

# If anomaly detected, log alert automatically if not already logged
if analysis["is_anomaly"] and analysis["severity"] in ["HIGH", "CRITICAL"]:
    if not alerts or alerts[0].get("event_type") != analysis["threat_name"]:
        collector.add_alert(
            event_type=analysis["threat_name"],
            severity=analysis["severity"],
            source_ip=telemetry.get("sender_ip", "127.0.0.1"),
            details=analysis["root_cause"]
        )

# Sidebar Controls & System Status
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shield.png", width=64)
    st.title("🛡️ SOC Control Room")
    st.caption("SIH 2026 | System Hackers Team")
    st.markdown("---")
    
    st.subheader("📡 Ingestion Status")
    st.write(f"• **Telemetry Port (UDP):** `5005`")
    st.write(f"• **Packets Processed:** `{telemetry.get('packets_received', 0)}`")
    st.write(f"• **Flow Rate:** `{telemetry.get('packet_rate_pps', 0)} pkts/s`")
    st.write(f"• **Data Diode Link:** `{'ACTIVE (Connected)' if telemetry.get('packets_received', 0) > 0 else 'AWAITING TELEMETRY'}`")
    
    st.markdown("---")
    st.subheader("⚡ Active Defense Actions")
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
    if auto_refresh:
        time.sleep(1.5)
        st.rerun()

# ----------------- MAIN SOC DASHBOARD ----------------- #

# 1. Top Security Alert Banner
if not analysis["is_anomaly"]:
    st.markdown(f"""
    <div class="soc-banner-safe">
        <div>
            <h2 style="margin:0; color:#10b981; font-size:1.5rem;">🟢 DEFCON 5 : ALL INDUSTRIAL PROCESSES NOMINAL</h2>
            <p style="margin:4px 0 0 0; color:#d1fae5; font-size:0.95rem;">One-Way Telemetry Flow Verified. ML Anomaly Score: <b>{analysis['anomaly_score']}%</b></p>
        </div>
        <div style="text-align:right;">
            <span style="background:#065f46; padding:6px 12px; border-radius:20px; font-weight:bold; color:#a7f3d0;">PROTECTED ACTIVE</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="soc-banner-danger">
        <div>
            <h2 style="margin:0; color:#ffffff; font-size:1.5rem;">🚨 ALERT: {analysis['threat_name']}</h2>
            <p style="margin:4px 0 0 0; color:#fecaca; font-size:0.95rem;">
                <b>Critical Process Deviation Detected!</b> Anomaly Confidence: <b>{analysis['anomaly_score']}%</b> | {analysis['mitre_id']}
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 2. Key Physical Telemetry Gauges (4 Metric Cards)
col1, col2, col3, col4 = st.columns(4)

with col1:
    rpm = telemetry.get("turbine_rpm", 3000.0)
    rpm_color = "#ef4444" if rpm > 4500 else "#38bdf8"
    st.markdown(f"""
    <div class="soc-card">
        <div class="soc-card-header">Turbine Generator Speed</div>
        <div class="soc-metric-val" style="color:{rpm_color};">{rpm:.1f} <span style="font-size:1rem;color:#94a3b8;">RPM</span></div>
        <div style="font-size:0.8rem; color:#64748b; margin-top:4px;">Nominal: 3000 RPM (Max: 4500)</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    psi = telemetry.get("boiler_psi", 125.0)
    psi_color = "#ef4444" if psi > 250 else "#38bdf8"
    st.markdown(f"""
    <div class="soc-card">
        <div class="soc-card-header">Steam Boiler Pressure</div>
        <div class="soc-metric-val" style="color:{psi_color};">{psi:.1f} <span style="font-size:1rem;color:#94a3b8;">PSI</span></div>
        <div style="font-size:0.8rem; color:#64748b; margin-top:4px;">Nominal: 125 PSI (Burst: 250)</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    temp = telemetry.get("reactor_temp", 72.5)
    temp_color = "#ef4444" if temp > 95.0 else "#38bdf8"
    st.markdown(f"""
    <div class="soc-card">
        <div class="soc-card-header">Reactor Core Temperature</div>
        <div class="soc-metric-val" style="color:{temp_color};">{temp:.1f} <span style="font-size:1rem;color:#94a3b8;">°C</span></div>
        <div style="font-size:0.8rem; color:#64748b; margin-top:4px;">Nominal: 72.5 °C (Hazard: 95.0)</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    flow = telemetry.get("coolant_flow", 82.0)
    flow_color = "#ef4444" if flow < 30.0 else "#38bdf8"
    st.markdown(f"""
    <div class="soc-card">
        <div class="soc-card-header">Coolant Circulation Flow</div>
        <div class="soc-metric-val" style="color:{flow_color};">{flow:.1f} <span style="font-size:1rem;color:#94a3b8;">L/min</span></div>
        <div style="font-size:0.8rem; color:#64748b; margin-top:4px;">Nominal: 82.0 L/min (Choke: <30)</div>
    </div>
    """, unsafe_allow_html=True)

# 3. Real-Time Telemetry Trend Charts & Threat Intelligence
chart_col, intel_col = st.columns([2, 1])

with chart_col:
    st.subheader("📈 Live Physical Telemetry Stream")
    
    if len(history) > 1:
        df = pd.DataFrame(history)
        
        # Plotly Time-Series Chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            y=df["turbine_rpm"],
            mode='lines+markers',
            name='Turbine RPM',
            line=dict(color='#38bdf8', width=2.5),
            yaxis='y1'
        ))
        fig.add_trace(go.Scatter(
            y=df["boiler_psi"],
            mode='lines',
            name='Boiler PSI',
            line=dict(color='#f59e0b', width=2, dash='dot'),
            yaxis='y2'
        ))
        
        fig.update_layout(
            paper_bgcolor='#0b111e',
            plot_bgcolor='#111c33',
            font=dict(color='#94a3b8'),
            margin=dict(l=20, r=20, t=30, b=20),
            height=320,
            xaxis=dict(showgrid=True, gridcolor='#1e293b', title="Recent Time Slices"),
            yaxis=dict(title="Turbine Speed (RPM)", titlefont=dict(color="#38bdf8"), tickfont=dict(color="#38bdf8"), showgrid=True, gridcolor='#1e293b'),
            yaxis2=dict(title="Boiler Pressure (PSI)", titlefont=dict(color="#f59e0b"), tickfont=dict(color="#f59e0b"), overlaying='y', side='right'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Awaiting telemetry stream from Laptop A (Port 5005)...")

with intel_col:
    st.subheader("🧠 Threat AI & MITRE ATT&CK")
    box_class = "threat-intel-danger" if analysis["is_anomaly"] else "threat-intel-box"
    
    st.markdown(f"""
    <div class="{box_class}">
        <div style="font-size:0.85rem; color:#94a3b8; font-weight:600;">ML THREAT CLASSIFICATION</div>
        <div style="font-size:1.15rem; font-weight:bold; color:#f8fafc; margin:4px 0;">{analysis['threat_name']}</div>
        <div style="font-size:0.85rem; color:#cbd5e1; margin-top:8px;">
            <b>• Severity:</b> <span style="color:{'#ef4444' if analysis['severity']=='CRITICAL' else '#10b981'};">{analysis['severity']}</span><br>
            <b>• MITRE Mapping:</b> {analysis['mitre_id']}<br>
            <b>• Anomaly Probability:</b> {analysis['anomaly_score']}%<br>
            <b>• Diagnosis:</b> {analysis['root_cause']}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="background:#111c33; border:1px solid #1e293b; border-radius:8px; padding:12px; margin-top:12px;">
        <div style="font-size:0.8rem; color:#94a3b8;">SPOOF / ATTACK INJECTOR SENDER</div>
        <div style="font-size:1rem; font-weight:600; color:#e2e8f0; margin-top:2px;">
            {telemetry.get('tampered_by', 'None (Clean Baseline)')}
        </div>
    </div>
    """, unsafe_allow_html=True)

# 4. Live Security Incident & Audit Log Table
st.markdown("---")
st.subheader("📋 Live Security Incident & Defense Audit Feed")

if alerts:
    alert_df = pd.DataFrame(alerts)
    st.dataframe(
        alert_df,
        use_container_width=True,
        column_config={
            "timestamp": "Time",
            "event_type": "Threat Event Signature",
            "severity": st.column_config.TextColumn("Severity", help="Incident Severity Level"),
            "source_ip": "Source IP",
            "details": "Root-Cause Forensic Analysis"
        },
        hide_index=True
    )
else:
    st.success("No critical security incidents recorded. System running clean.")
