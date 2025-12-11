# AURA Project Analysis

## Project Summary
AURA is an AI-driven proactive cybersecurity framework designed to autonomously defend modern IT and IoT infrastructures. It integrates Intrusion Detection (IDS), Open-Source Intelligence (OSINT), and Deception Technology (Honeypots) into a unified, closed-loop system. The system forecasts emerging threats and dynamically configures decoys to trap attackers, aiming to solve "alert fatigue" and improve resilience against sophisticated threats.

## Project Objectives
1.  **AI-Based Detection**: Develop a real-time Intrusion Detection System (IDS) using machine learning (CNN + BiLSTM).
2.  **Contextual Awareness**: Integrate OSINT-driven threat intelligence to enrich alerts with external data.
3.  **Unified Framework**: Unify detection, intelligence, and response within a single architecture to calculate a "Final Threat Score".
4.  **Autonomous Response**: Implement adaptive response mechanisms (blocking, redirection) and dynamic deception.
5.  **Explainability & Scalability**: Provide real-time, explainable cyber defense capabilities.

## Module Analysis
The project is divided into four interconnected layers:

### Module 1: OSINT Harvester (Intelligence Layer)
*   **Status**: Functional Prototype
*   **Key Files**: `main.py`, `live_threat_feeds.py`, `threat_forecaster.py`, `correlator.py`
*   **Functionality**: Fetches data from Reddit, GitHub, and CISA; calculates trending scores; correlates PoCs with NVD/CISA data; extracts IOCs.

### Module 2: AI-Based IDS Engine (Detection Layer)
*   **Status**: Architecture Validated & Designed (Implementation Pending)
*   **Planned Architecture**: Hybrid CNN + BiLSTM model trained on UM-NIDS dataset.
*   **Input**: Network traffic (PCAP) and System Logs.
*   **Output**: Prediction label (e.g., Normal, DDoS, SQLi) with confidence score.

### Module 3: Dynamic Deception (Honeypot Layer)
*   **Status**: Static Honeypot Deployed (Integration Pending)
*   **Component**: Cowrie (SSH/Telnet honeypot).
*   **Goal**: Dynamically reconfigure based on OSINT intel.

### Module 4: Automated Response & Retraining (Action Layer)
*   **Status**: In Development (Rule-based engine)
*   **Workflow**: Threat Scoring Engine -> Response Engine -> Adaptive Learning Loop.

## Key Features
*   **Unified Closed-Loop System**: Feedback loop where intelligence informs detection, detection triggers deception, and deception data retrains intelligence.
*   **Multimodal Detection**: Analysis of flow statistics and payload data.
*   **Threat Forecasting**: Identifies "trending" threats using social platform momentum.
*   **Intelligence-Driven Deception**: Dynamic honeypot configuration based on high-profile threats.

## Next Steps (Roadmap)
1.  **Phase 1: Build the AI-IDS Engine** (High Priority)
    *   Create `ids_module/`.
    *   Implement data ingestion (UM-NIDS/CIC-IDS).
    *   Implement feature engineering and OSINT injection.
    *   Train CNN+BiLSTM model.
    *   Create Inference API.
2.  **Phase 2: Dynamic Honeypot Integration**
    *   Create `honeypot_manager.py`.
    *   Bridge `osint-harvester` with Cowrie.
3.  **Phase 3: The Unified Dashboard**
    *   Build a web dashboard (Streamlit/React) to visualize live feeds, threat scores, and system status.
