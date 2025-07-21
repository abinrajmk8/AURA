# AURA
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
git clone https://github.com/abinrajmk8/AURA.git
cd AURA
```

### 2. Create and Activate a Virtual Environment   (creation- only once )
for linux
```bash
python3 -m venv venv
source venv/bin/activate        -
```

for windows
```bash
python3 -m venv venv
venv\Scripts\activate           
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Navigate to the Harvester Module
```bash
cd osint-harvester
```

### 5. Paste the .env file in osint-harvester folder

### 6. Run the OSINT Harvester
```bash
python main.py --poc 
```

also try other  command line arguments

---





---

> Designed and maintained by the AURA Research Team – 
