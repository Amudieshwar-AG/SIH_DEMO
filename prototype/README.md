# 🛡️ SIH 2026 : ICS/SCADA 3-Laptop Cyber-Physical Defense Prototype

> **Team:** System Hackers  
> **Architecture:** 3-Node Industrial Cyber-Defense Grid with Data Diode Telemetry, AI Anomaly Detection & MITRE ATT&CK Classification.

---

## 📐 System Architecture Overview

```
              ┌───────────────────────────┐
              │         LAPTOP A          │
              │  PROTECTED PLANT (ICS)    │
              │  • Steam Boiler Simulator │
              │  • Turbine & Reactor Core │
              │  • Modbus/PLC Logic Loop  │
              └─────────────┬─────────────┘
                            │
                            │ UDP Telemetry (Port 5005)
                            │ [One-Way Data Diode Stream]
                            ▼
              ┌───────────────────────────┐
              │         LAPTOP B          │
              │    SOC DEFENSE HUB        │
              │  • Live UDP Flow Ingester │
              │  • ML Isolation Forest    │
              │  • Threat Classifier Engine│
              │  • Streamlit Cyber SOC UI │
              └─────────────▲─────────────┘
                            │
                            │ Simulated Attacks & Injections
                            │ (Ports 5002 & 5006)
              ┌─────────────┴─────────────┐
              │         LAPTOP C          │
              │    ATTACK & THREAT GEN    │
              │  • Stuxnet Turbine Spoof  │
              │  • Boiler Overpressure    │
              │  • Coolant Choke Attack   │
              │  • Volumetric UDP Flood   │
              └───────────────────────────┘
```

---

## ⚡ Option 1: Test Everything on 1 Laptop (Fastest - 10 Seconds)

To verify the prototype right now on your current machine:
1. Open the folder: `d:\SIH 2026\prototype\`
2. Double-click **`start_all_local.bat`**
3. It will open 3 windows automatically:
   * **Window 1:** Laptop A Plant Terminal
   * **Window 2:** Laptop B SOC Dashboard (Open `http://localhost:8502` in your browser)
   * **Window 3:** Laptop C Attack Console (Press `2`, `3`, or `4` to test attack injections!)

---

## 🌐 Option 2: Run Across 3 Separate Laptops (For Tomorrow's Stage Presentation)

### Step 1: Network Setup (Takes 1 Minute)
1. Connect all 3 laptops to the **same Wi-Fi network or Mobile Hotspot**.
2. On **Laptop B** (SOC), open Command Prompt and type:
   ```bash
   ipconfig
   ```
   Note the IPv4 address (e.g., `192.168.1.45`).
3. On **Laptop A** (Plant), note its IPv4 address (e.g., `192.168.1.30`).

---

### Step 2: Launch in Order

#### 1. On Laptop B (SOC Defense Hub):
* Open folder `prototype/laptop_b_soc/`
* Double-click **`run_laptop_b.bat`** (or run `streamlit run app.py --server.port 8502`)
* Browser will automatically open the **SOC Defense Dashboard**.

#### 2. On Laptop A (Protected Plant):
* Open folder `prototype/laptop_a_plant/`
* Double-click **`run_laptop_a.bat`** (or run `python plant_sim.py`)
* When prompted: enter **Laptop B's IP** (e.g. `192.168.1.45`).
* You will see the green terminal monitor broadcasting live telemetry.

#### 3. On Laptop C (Attacker / Threat Injector):
* Open folder `prototype/laptop_c_attacker/`
* Double-click **`run_laptop_c.bat`**
* Enter **Laptop A's IP** (for plant attacks) and **Laptop B's IP** (for flood attacks).
* Choose option `1` (Terminal Console) or `2` (Web Cyber UI at port `8503`).

---

## 🎤 3-Minute Live Presentation Script for Judges

| Time | Action | What to Say to the Judges |
| :--- | :--- | :--- |
| **0:00 - 0:45** | Show **Laptop A & B** running | *"Good morning respected judges. We are Team System Hackers. In critical infrastructure like power plants and nuclear facilities, traditional IT firewalls fail because SCADA and PLC devices run proprietary OT protocols. On Laptop A, we are simulating a live power plant. Notice it emits one-way UDP telemetry to Laptop B via an emulated hardware Data Diode. On Laptop B, our ML engine establishes a baseline of normal operation."* |
| **0:45 - 1:30** | Press `[2]` on **Laptop C** (*Stuxnet Turbine Attack*) | *"Now, on Laptop C, we simulate a sophisticated APT adversary injecting an unauthorized PLC setpoint override (similar to the historic Stuxnet attack). We fire an over-speed command to Laptop A."* |
| **1:30 - 2:15** | Switch judge's eyes to **Laptop B** | *"Watch Laptop B's SOC dashboard. Within 1 second, our Isolation Forest and Threat Classifier detect the mechanical anomaly. The alert banner flashes RED, classifies the threat under MITRE ATT&CK T0836 (Modify Parameter), and pinpoints the exact attack source without human intervention."* |
| **2:15 - 3:00** | Click **"TRIGGER DATA-DIODE ISOLATION"** on Laptop B | *"Our system can immediately execute automated failsafe isolation to prevent catastrophic physical meltdown. We can also detect volumetric network sensor jamming by pressing option 5 on Laptop C."* |

---

## 🛡️ Attack Scenarios Matrix

| Key | Attack Scenario | Target Node | MITRE ATT&CK Technique | Expected Reaction on Laptop B |
| :---: | :--- | :---: | :--- | :--- |
| **1** | Safe Normal Baseline | Laptop A | Normal Operations | Dashboard stays Green / DEFCON 5 |
| **2** | Stuxnet Turbine Over-speed | Laptop A | `T0836` Modify Parameter | Turbine speed spikes to ~5,850 RPM -> Critical Alert |
| **3** | Boiler Overpressure | Laptop A | `T0846` Impair Process | Pressure surges to 420 PSI -> Red Alert |
| **4** | Coolant Starvation | Laptop A | `T0806` Brute Force I/O | Coolant drops to 4 L/min, core temp exceeds 100°C |
| **5** | Volumetric UDP DDoS | Laptop B | `T0814` Denial of Service | Packet rate surges to 60+ pkts/s -> DDoS Detected |
