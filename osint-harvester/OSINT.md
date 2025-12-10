# AURA OSINT Harvester Module

## 1. Overview
The **AURA OSINT Harvester** is a specialized module designed to autonomously collect, analyze, and standardize threat intelligence from various open sources. It serves as the "eyes and ears" of the AURA system, feeding high-quality, structured data into the Intrusion Detection System (IDS).

Unlike traditional feed aggregators, this module leverages **Generative AI (Google Gemini)** to deeply analyze raw Proof-of-Concept (PoC) code, extracting actionable "Micro-Rules" and attack signatures that can be immediately used for active defense.

## 2. Objectives
*   **Automated Collection**: Aggregate threat data from diverse sources (Social Media, Code Repositories, Government Feeds).
*   **Deep Analysis**: Go beyond metadata. Analyze the *actual code* of exploits to understand how they work.
*   **Actionable Intelligence**: Convert raw data into structured formats (JSON) with specific fields like `Target`, `Payload`, and `Micro-Rule`.
*   **Rate-Limit Resilience**: Operate effectively within API quotas (e.g., Gemini Free Tier) using optimized consolidation strategies.

## 3. Key Features

### 🌐 Multi-Source Collection
*   **Reddit (`r/netsec`)**: Tracks social trends and discussions to identify emerging threats before they have CVEs.
*   **GitHub**: Searches for and downloads raw Proof-of-Concept (PoC) repositories for recent vulnerabilities.
*   **CISA KEV**: Fetches the Known Exploited Vulnerabilities catalog for verified, high-priority threats.

### 🧠 AI-Powered Analysis (Gemini Integration)
*   **Holistic Repo Analysis**: Instead of analyzing files individually (which hits rate limits), the system consolidates critical files (`app.py`, `main.py`, `README.md`) into a single context block.
*   **Structured Extraction**: The AI is prompted to extract:
    *   **Target Endpoint**: Where the attack is directed (e.g., `/admin/upload`).
    *   **Attack Payload**: The specific malicious string or byte sequence.
    *   **Attack Type**: Classification (RCE, SQLi, XSS, etc.).
    *   **Micro-Rule**: A generated Regex or Snort-like signature for blocking.

### ⚙️ Robust Standardization
*   **Unified Format**: All data, regardless of source, is normalized into a standard JSON structure.
*   **Tagging & Confidence**: Every entry is assigned a confidence score and relevant tags (e.g., `active_defense`, `high_confidence`).
*   **Legacy Support**: Falls back to Regex-based parsing if AI is unavailable or fails.

## 4. Architecture

The module operates in a linear pipeline:

1.  **Fetcher (`main.py`)**: Orchestrates the collection from Reddit, GitHub, and CISA.
2.  **Parser (`github_poc_parser/`)**:
    *   Clones repositories.
    *   **`parser.py`**: Performs Regex extraction (IPs, URLs) and prepares content for AI.
    *   **`ai_parser.py`**: Handles communication with the Google Gemini API.
3.  **Standardizer (`utils/standardizer.py`)**:
    *   Reads raw outputs (`refined_poc.json`, `ai_insights.json`).
    *   Merges AI insights with standard indicators.
    *   Produces the final `intelligence_feed.json`.

## 5. Installation & Setup

### Prerequisites
*   Python 3.10+
*   Google Gemini API Key

### Environment Variables
Create a `.env` file in the `osint-harvester` directory:
```bash
GEMINI_API_KEY="your_google_api_key_here"
# Optional: Reddit API credentials if you want to use the Reddit fetcher heavily
# REDDIT_CLIENT_ID="..."
# REDDIT_CLIENT_SECRET="..."
```

### Dependencies
```bash
pip install -r requirements.txt
```

## 6. Usage Guide

The module is run via the `main.py` script.

### Basic Harvest (Live Feeds)
Collects metadata from Reddit, GitHub (metadata only), and CISA.
```bash
python3 main.py --live
```

### Full Harvest (with AI Analysis)
Collects feeds AND downloads/analyzes GitHub PoC code using Gemini.
*Note: This respects rate limits by processing one repo at a time by default.*
```bash
python3 main.py --live --poc
```

### Filtering
Target specific keywords or severity levels.
```bash
python3 main.py --keyword "wordpress" --severity "CRITICAL" --live
```

## 7. Output Files

All output is stored in the `data/` directory:

| File | Description |
| :--- | :--- |
| **`intelligence_feed.json`** | **The Master Feed.** Contains standardized entries from ALL sources, including AI rules. This is what the IDS consumes. |
| `parsed/refined_poc.json` | Detailed output from the Regex parser (IPs, URLs, etc.). |
| `parsed/ai_insights.json` | Raw, high-quality insights extracted by Gemini (Micro-rules, Payloads). |
| `reddit_posts.json` | Raw data from Reddit. |
| `cisa_vulns.json` | Raw data from CISA. |

## 8. Troubleshooting

### `429 RESOURCE_EXHAUSTED` (Gemini API)
*   **Cause**: You have exceeded the free tier rate limit (Requests Per Minute).
*   **Solution**: The system is designed to handle this gracefully. It will log the error and continue with Regex parsing. To get AI insights, wait ~60 seconds and run the command again.

### `FileNotFoundError: data/github_repos.json`
*   **Cause**: You tried to run `--poc` without first fetching the repo list.
*   **Solution**: Run with `--live` first (or together with `--poc`) to populate the repo list.
    *   `python3 main.py --live --poc`

## 9. Future Roadmap
*   **Embedding Generation**: Re-enable vector embeddings for semantic search once a paid API tier or local model is available.
*   **Expanded Sources**: Add Twitter/X scraping or RSS feeds.
*   **Real-time Stream**: Convert the batch process into a continuous listening daemon.
