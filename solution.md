# AURA Solution Design: OSINT & IDS Fusion

## 1. Effective Use of OSINT (Beyond IPs)
While IP addresses are common Indicators of Compromise (IOCs), they are ephemeral. To make OSINT effective in a real-time IDS, we must leverage more persistent indicators.

### A. Pattern & Keyword Matching (Payload Analysis)
*   **Concept**: Your OSINT harvester extracts keywords (e.g., "log4j", "jndi", specific shellcode bytes) from PoCs.
*   **Usage**: The IDS analyzes the **payload** of packets. If a payload contains a string or byte sequence found in your OSINT "Trending Keywords" database, it flags the traffic.
*   **Implementation**: Maintain a fast Aho-Corasick dictionary of trending strings. Check HTTP bodies and TCP payloads against this dictionary.

### B. Port & Protocol Context (Vulnerability Mapping)
*   **Concept**: OSINT tells you *which* services are currently under attack (e.g., "New CVE in WebLogic on port 7001").
*   **Usage**: If OSINT shows a spike in exploits for Port X, the IDS treats *any* anomaly on Port X with higher severity.
*   **Implementation**: A "Threat Heatmap" (e.g., `{Port: 80, ThreatLevel: High}`).

### C. Behavioral Correlation
*   **Concept**: OSINT descriptions often mention behavior (e.g., "User-Agent: python-requests" combined with "POST /api/v1/login").
*   **Usage**: Match metadata combinations, not just single fields.

## 2. Fusion Logic: Combining Scores
We will use a **Late Fusion (Post-Processing)** approach. This separates the "Anomaly Detection" (IDS) from the "Contextual Intelligence" (OSINT), making the system more robust.

### The Formula: Final Threat Score
$$ S_{final} = \alpha \cdot S_{IDS} + \beta \cdot S_{OSINT} + \gamma \cdot C_{Trend} $$

Where:
*   **$S_{IDS}$ (0.0 - 1.0)**: The confidence score from your CNN+BiLSTM model.
*   **$S_{OSINT}$ (0.0 - 1.0)**: A score based on matching IOCs (IP, Hash, Keyword).
*   **$C_{Trend}$ (0.0 - 1.0)**: A multiplier based on global threat trends (from `threat_forecaster.py`).
*   **Weights ($\alpha, \beta, \gamma$)**: Tunable parameters.
    *   *Recommendation*: $\alpha=0.6$ (Model is primary), $\beta=0.3$ (Intel confirmation), $\gamma=0.1$ (Trend awareness).

### Decision Thresholds
*   **Score > 0.8**: **BLOCK** (High confidence attack).
*   **Score 0.5 - 0.8**: **REDIRECT** (Suspicious -> Send to Honeypot).
*   **Score < 0.5**: **ALLOW** (Normal).

## 3. Integration Points
We will implement integration at two distinct levels:

### Level 1: Dynamic Thresholding (Pre-Detection)
*   **Logic**: "If OSINT says SSH attacks are trending, be more paranoid about SSH."
*   **Mechanism**: The IDS has a default threshold of 0.8 for alerting. If `port == 22` AND `trend_score["SSH"] > 0.9`, lower the alert threshold to 0.6.
*   **Benefit**: Increases sensitivity for high-risk vectors without retraining the model.

### Level 2: Alert Enrichment (Post-Detection)
*   **Logic**: The IDS detects an anomaly. Before showing it to the user, we query the OSINT database.
*   **Mechanism**:
    1.  IDS detects "Abnormal Flow" (Score: 0.7).
    2.  System checks OSINT DB:
        *   Is Source IP in blocklist? (No)
        *   Does Payload contain trending keywords? (Yes, found "Exploit-X").
    3.  **Boost Score**: $0.7 + 0.2 (\text{Keyword Match}) = 0.9$.
    4.  **Action**: Block.

## 4. Proposed Architecture Changes

### A. Standardize OSINT Output
We need a uniform JSON structure for all OSINT feeds to make ingestion easy.
**Target Format (`data/intelligence_feed.json`):**
```json
[
  {
    "type": "ipv4",
    "value": "192.168.1.5",
    "confidence": 0.9,
    "tags": ["scanner", "mirai"],
    "last_seen": "2023-10-27T10:00:00Z"
  },
  {
    "type": "keyword",
    "value": "${jndi:ldap}",
    "confidence": 1.0,
    "related_cve": "CVE-2021-44228",
    "target_ports": [80, 443, 8080]
  }
]
```

### B. The "Fusion Engine" Module
A new Python class `FusionEngine` that sits between the IDS and the Response System.
*   **Input**: Packet Metadata, IDS Prediction.
*   **Process**: Lookups in `intelligence_feed.json`.
*   **Output**: Final Decision (Block/Redirect/Log).

## Summary of Next Steps
1.  **Standardize**: Refactor `osint-harvester` to output the standard JSON format above.
2.  **Implement IDS**: Build the CNN+BiLSTM model (as planned).
3.  **Build Fusion Engine**: Implement the scoring logic and dynamic thresholding.
