# AURA IDS - Usage Guide

This guide explains how to run the Intrusion Detection System (IDS) and the Attack Simulator.

## Prerequisites

*   **Root/Sudo Privileges**: Required for packet sniffing (IDS) and packet injection (Simulator).
*   **Python Environment**: Ensure dependencies are installed (scapy, rich, pandas, numpy, joblib, lightgbm).
*   **Working Directory**: Run all commands from the **project root** (`/home/abin/Desktop/project/AURA/`).

## 1. Running the IDS (Defender)

The IDS listens for network traffic, analyzes it against OSINT rules and the ML model, and alerts on threats.

**Command:**
Since `scapy` requires root privileges (`sudo`), you must point `sudo` to the Python executable *inside* your virtual environment, otherwise it will try to use the system Python (which doesn't have the dependencies installed).

```bash
sudo ./venv/bin/python3 IDS/main.py -i <interface>
```

*   **Local Testing (with Simulator):** Use the loopback interface (`lo`).
    ```bash
    sudo ./venv/bin/python3 IDS/main.py -i lo
    ```
*   **Real Network Monitoring:** Use your active network interface (e.g., `eth0`, `wlan0`).
    ```bash
    sudo ./venv/bin/python3 IDS/main.py -i wlan0
    ```

**Output:**
*   `[*] Starting Sniffer...` indicates it's running.
*   **ALERTS** (Orange) indicate suspicious behavior detected by the ML model.
*   **BLOCKS** (Red) indicate known threats matched against the OSINT feed.

## 2. Running the Attack Simulator (Attacker)

The simulator sends malicious packets to `localhost` to test the IDS detection capabilities.

**Command:**
```bash
sudo ./venv/bin/python3 IDS/attacker_sim.py
```

**What it does:**
1.  **OSINT Test**: Sends a packet with a malicious payload (`OGNL:whoami`) to test rule-based detection.
2.  **DoS Test**: Floods the target with 500 UDP packets to test flow-based anomaly detection.

## 3. End-to-End Test Workflow

1.  Open **Terminal 1** (IDS):
    ```bash
    cd /home/abin/Desktop/project/AURA
    sudo ./venv/bin/python3 IDS/main.py -i lo
    ```
2.  Open **Terminal 2** (Attacker):
    ```bash
    cd /home/abin/Desktop/project/AURA
    sudo ./venv/bin/python3 IDS/attacker_sim.py
    ```
3.  **Observe Terminal 1**:
    *   You should see a **BLOCK** alert for the OGNL payload.
    *   You should see an **ALERT** for the DoS attack (ML Anomaly).
