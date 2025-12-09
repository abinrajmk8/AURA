import json
import os
from datetime import datetime

class Standardizer:
    def __init__(self, data_dir="./data"):
        self.data_dir = data_dir
        self.feed = []

    def load_json(self, filename):
        path = os.path.join(self.data_dir, filename)
        if os.path.exists(path):
            with open(path, 'r') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return []
        return []

    def standardize_reddit(self):
        data = self.load_json("reddit_posts.json")
        for item in data:
            # Reddit mainly gives us trending keywords/CVEs in titles
            # We extract them as "keyword" or "cve" type
            self.feed.append({
                "value": item.get("title", "")[:100], # Truncate for safety
                "type": "social_trend",
                "source": "reddit",
                "confidence": 0.3, # Low confidence as it's just a post
                "tags": ["netsec", "discussion"],
                "last_seen": item.get("created", datetime.now().isoformat())
            })

    def standardize_cisa(self):
        data = self.load_json("cisa_vulns.json")
        for item in data:
            self.feed.append({
                "value": item.get("cveID"),
                "type": "cve",
                "source": "cisa_kev",
                "confidence": 1.0, # High confidence (Confirmed Exploited)
                "tags": ["kev", "exploit_known"],
                "last_seen": item.get("dateAdded", datetime.now().isoformat())
            })

    def standardize_poc_parser(self):
        # This is the most valuable file
        data = self.load_json("parsed/poc_output.json")
        
        if not isinstance(data, dict):
            # If file missing or empty list, skip
            return

        # The parser output structure is: {"files_parsed": [], "iocs": {...}}
        iocs = data.get("iocs", {})
        
        for ip in iocs.get("ips", []):
            self.feed.append({
                "value": ip,
                "type": "ipv4",
                "source": "github_poc",
                "confidence": 0.7,
                "tags": ["potential_attacker", "poc_related"],
                "last_seen": datetime.now().isoformat()
            })
            
        for url in iocs.get("urls", []):
            self.feed.append({
                "value": url,
                "type": "url",
                "source": "github_poc",
                "confidence": 0.6,
                "tags": ["poc_related"],
                "last_seen": datetime.now().isoformat()
            })
            
        for kw in iocs.get("keywords", []):
            self.feed.append({
                "value": kw,
                "type": "keyword",
                "source": "github_poc",
                "confidence": 0.8,
                "tags": ["attack_vector", "payload_signature"],
                "last_seen": datetime.now().isoformat()
            })

    def standardize_forecast(self):
        data = self.load_json("forecast.json")
        for item in data:
            self.feed.append({
                "value": item.get("cve_id"),
                "type": "cve",
                "source": "threat_forecast",
                "confidence": 0.5 + (item.get("trending_score", 0) / 100), # Normalize score
                "tags": ["trending", "high_risk"],
                "last_seen": datetime.now().isoformat()
            })

    def run(self):
        self.standardize_reddit()
        self.standardize_cisa()
        self.standardize_poc_parser()
        self.standardize_forecast()
        
        output_path = os.path.join(self.data_dir, "intelligence_feed.json")
        with open(output_path, 'w') as f:
            json.dump(self.feed, f, indent=2)
        print(f"[+] Standardized intelligence feed saved to {output_path} with {len(self.feed)} entries.")

if __name__ == "__main__":
    std = Standardizer()
    std.run()
