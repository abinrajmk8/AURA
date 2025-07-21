#AURA
module 1 
## AURA: OSINT Threat Harvester

> **Part of AURA (Adaptive Unified Response Agent)**  
>  Real-time, AI-assisted OSINT harvesting and threat correlation system

##  Overview

The **OSINT Threat Harvester** is a key component of the AURA cybersecurity suite. It continuously monitors open-source platforms like **Reddit**, **GitHub**, and **CISA KEV** for emerging cybersecurity threats, Proof-of-Concepts (PoCs), and Indicators of Compromise (IOCs). Extracted data is parsed, correlated, and exported in structured formats for downstream threat intelligence workflows.

Key Features:
- Live scraping from GitHub repos, Reddit threads, and CISA KEV
- PoC and IOC extraction from code/README files
- Structured output in JSON/CSV
- Modular & extensible for future LLM/NLP integration
- CLI-friendly & research-grade

---

##  Setup Instructions

Follow these steps to install and run the OSINT Threat Harvester:

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/aura-osint-harvester.git
cd aura-osint-harvester
```

### 2. Create and Activate a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate        # For Linux/macOS
# OR
venv\Scripts\activate           # For Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Navigate to the Harvester Module
```bash
cd osint_harvester
```

### 5. Run the OSINT Harvester
```bash
python main.py
```

---





---

> Designed and maintained by the AURA Research Team – 
