# OSINT Harvester Analysis Report

## 1. Current Status
The `osint-harvester` module is functional but fragmented. It successfully fetches data from multiple sources but stores them in isolated, inconsistent formats.

### Existing Outputs
*   **Reddit Feed** (`data/reddit_posts.json`): Contains `title`, `url`, `score`, `created`. Good for trend analysis but lacks direct IOCs.
*   **GitHub Feed** (`data/github_repos.json`): Contains `name`, `url`, `updated`.
*   **CISA KEV** (`data/cisa_vulns.json`): Structured CVE data.
*   **Threat Forecast** (`data/forecast.json`): Contains `cve_id` and `trending_score`.
*   **PoC Parser** (`data/parsed/poc_output.json`): **Crucial Component**. It *does* extract IPs, URLs, Base64, and Keywords, but this data is siloed.

### Issues
1.  **Non-Standard Output**: The IDS cannot consume 5 different JSON schemas. It needs one.
2.  **Missing Context**: A list of IPs in `poc_output.json` doesn't tell us *why* they are bad (e.g., are they scanners? C2 servers?).
3.  **No "Fusion" Readiness**: The current output is raw data, not "Intelligence".

## 2. Required Changes
To enable the "Fusion Logic" described in `solution.md`, we must transform these raw feeds into a **Unified Intelligence Feed**.

### A. New Data Schema
We will enforce the following schema for `data/intelligence_feed.json`:

```json
[
  {
    "value": "192.168.1.5",
    "type": "ipv4",
    "source": "github_poc_parser",
    "confidence": 0.8,
    "tags": ["scanner", "CVE-2023-1234"],
    "last_seen": "2023-12-09"
  },
  {
    "value": "log4j",
    "type": "keyword",
    "source": "reddit_trend",
    "confidence": 0.9,
    "tags": ["payload", "java"],
    "last_seen": "2023-12-09"
  }
]
```

### B. Implementation Plan
1.  **Create `standardizer.py`**: A new script to read all existing JSONs and convert them to the new schema.
2.  **Update `main.py`**: Integrate the standardizer to run automatically after fetching/parsing.
3.  **Enhance `threat_forecaster.py`**:
    *   Currently, it only calculates scores.
    *   **Change**: It should output "High Risk CVEs" as "keyword" type entries in the unified feed (e.g., value="CVE-2023-XXXX").

## 3. Execution Steps
1.  **Refactor**: Create `utils/standardizer.py`.
2.  **Modify**: Update `main.py` to call the standardizer.
3.  **Verify**: Run the harvester and check `data/intelligence_feed.json`.
