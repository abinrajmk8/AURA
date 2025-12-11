# AURA IDS Solution & Design

## 1. Analysis of Existing Resources
We have analyzed the `IDS` folder and the `Aura_nids.ipynb` notebook. Here is the assessment:

*   **Model**: LightGBM Classifier (`aura_ids_lightgbm.pkl`).
*   **Dataset**: CIC-IDS-2017 (High-quality, modern network traffic dataset).
*   **Preprocessing**: Standard Scaling (`scaler.pkl`) and Label Encoding (`label_encoder.pkl`).
*   **Performance**: LightGBM is excellent for tabular flow data, offering high speed and accuracy.
*   **Current State**: The notebook represents a *training* pipeline, not a *deployment* system. It processes static CSV files, not live traffic.

## 2. Can we use OSINT and IDS together?
**YES.** They are perfectly complementary.

*   **OSINT Harvester (The "Watchlist")**:
    *   **Function**: Provides specific, known indicators of compromise (IOCs).
    *   **Action**: "Block traffic from IP 1.2.3.4" or "Block requests containing `OGNL:whoami`".
    *   **Speed**: Extremely fast (Hash lookup / Regex match).
    *   **Limitation**: Can only stop *known* threats.

*   **ML IDS (The "Brain")**:
    *   **Function**: Analyzes traffic behavior (flow duration, packet size, inter-arrival times).
    *   **Action**: "This traffic flow looks like a DDoS attack" or "This SSH session looks like a Brute Force attempt".
    *   **Speed**: Slower (Requires feature extraction + inference).
    *   **Advantage**: Can stop *unknown* (Zero-Day) threats if they behave anomalously.

## 3. Real-Time Implementation Strategy
To convert the static model into a real-time system, we need to build a **Traffic Pipeline**:

### Architecture
1.  **Packet Sniffer**: Use `scapy` or `pyshark` to capture live network packets.
2.  **Flow Feature Extractor**: This is the critical component. The model expects 78 specific features (e.g., `Flow Duration`, `Total Fwd Packets`). We must calculate these in real-time from the raw packets.
    *   *Tool*: We will implement a Python-based **FlowMeter** (inspired by `cicflowmeter`) to aggregate packets into flows and calculate statistics.
3.  **Hybrid Detection Engine**:
    *   **Step 1 (OSINT Check)**: Check Source IP/URL against `intelligence_feed.json`. If match -> **ALERT/BLOCK**.
    *   **Step 2 (ML Check)**: If OSINT passes, send the flow features to the LightGBM model. If `Prediction == ATTACK` -> **ALERT**.

## 4. Proposed Directory Structure
```
IDS/
├── models/
│   ├── aura_ids_lightgbm.pkl
│   ├── scaler.pkl
│   └── label_encoder.pkl
├── core/
│   ├── sniffer.py        # Captures packets
│   ├── flow_generator.py # Calculates CIC-2017 features
│   └── detector.py       # Loads model & OSINT feed, makes decisions
├── main.py               # Entry point
└── requirements.txt
```

## 5. Implementation Plan

### Phase 1: Setup & Loading
*   Create the directory structure.
*   Write a script to load the `.pkl` files and verify they work on dummy data.

### Phase 2: Feature Extraction (The Hard Part)
*   Implement `FlowSession` class to track active connections.
*   Calculate basic stats (Packet count, Length mean/std/max).
*   *Note: We may simplify the feature set if calculating all 78 features in real-time is too slow for Python, or we will use a subset that the model heavily relies on (using SHAP values from the notebook).*

### Phase 3: Integration
*   Load `../data/intelligence_feed.json`.
*   Build the main loop: `Sniff -> Aggregate -> Check OSINT -> Check ML -> Report`.

## 6. Conclusion
We can absolutely reuse your trained model. The primary challenge is engineering the **Real-time Feature Extractor** to match the training data format exactly. We will proceed by building this pipeline.
