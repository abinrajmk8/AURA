import json
import re
import os

def extract_cve_from_text(text):
    match = re.search(r"CVE-\d{4}-\d{4,7}", text, re.IGNORECASE)
    return match.group(0) if match else None

def load_repos_from_feed(feed_path="./data/github_repos.json"):
    if not os.path.exists(feed_path):
        raise FileNotFoundError(f"Feed not found at: {feed_path}")

    with open(feed_path) as f:
        entries = json.load(f)

    repos = []
    for item in entries:
        cve = extract_cve_from_text(item.get("name", "")) or extract_cve_from_text(item.get("url", ""))
        if cve:
            repos.append({
                "cve": cve,
                "repo_url": item["url"]
            })
    return repos
