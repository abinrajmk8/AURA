import json
import os
import sys
from datetime import datetime

# Ensure we can import from the same directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from ai_parser import AIParser
except ImportError:
    # Fallback if running from root
    from utils.ai_parser import AIParser

class Standardizer:
    def __init__(self, data_dir="./data"):
        self.data_dir = data_dir
        self.feed = []
        # We keep AIParser initialized but won't use it for embeddings anymore
        # We can use it for on-demand analysis if needed, but for now we just standardize
        # what we have collected.
        
    def load_json(self, filename):
        path = os.path.join(self.data_dir, filename)
        if os.path.exists(path):
            with open(path, 'r') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return []
        return []

    def add_entry(self, value, type, source, confidence, tags, last_seen, description="", extra_data=None):
        entry = {
            "value": value,
            "type": type,
            "source": source,
            "confidence": confidence,
            "tags": tags,
            "last_seen": last_seen,
            "description": description
        }
        if extra_data:
            entry.update(extra_data)
            
        self.feed.append(entry)

    def standardize_reddit(self):
        data = self.load_json("reddit_posts.json")
        print(f"Processing {len(data)} Reddit entries...")
        for item in data:
            self.add_entry(
                value=item.get("title", "")[:100],
                type="social_trend",
                source="reddit",
                confidence=0.3,
                tags=["netsec", "discussion"],
                last_seen=item.get("created", datetime.now().isoformat())
            )

    def standardize_cisa(self):
        data = self.load_json("cisa_vulns.json")
        print(f"Processing {len(data)} CISA entries...")
        for item in data:
            self.add_entry(
                value=item.get("cveID"),
                type="cve",
                source="cisa_kev",
                confidence=1.0,
                tags=["kev", "exploit_known"],
                last_seen=item.get("dateAdded", datetime.now().isoformat()),
                description=item.get("shortDescription", "")
            )

    def standardize_poc_parser(self):
        data = self.load_json("parsed/refined_poc.json")
        
        # Handle list format (new)
        if isinstance(data, list):
            for entry in data:
                iocs = entry.get("iocs", {})
                self._process_iocs(iocs)
                
                # Also process AI insights if available directly
                ai_insights = entry.get("ai_insights", [])
                for insight in ai_insights:
                     if insight.get("micro_rule"):
                         self.add_entry(
                            value=insight["micro_rule"],
                            type="micro_rule",
                            source="gemini_ai",
                            confidence=0.9,
                            tags=["active_defense", "generated_rule"],
                            last_seen=datetime.now().isoformat(),
                            description=f"Generated rule for {entry.get('cve_id', 'unknown')}"
                        )

        # Handle legacy dict format (old)
        elif isinstance(data, dict):
            self._process_iocs(data.get("iocs", {}))

    def _process_iocs(self, iocs):
        # Process IPs
        for ip in iocs.get("ips", []):
            self.add_entry(
                value=ip,
                type="ipv4",
                source="github_poc",
                confidence=0.7,
                tags=["potential_attacker", "poc_related"],
                last_seen=datetime.now().isoformat()
            )
            
        # Process URLs
        for url in iocs.get("urls", []):
            self.add_entry(
                value=url,
                type="url",
                source="github_poc",
                confidence=0.6,
                tags=["poc_related"],
                last_seen=datetime.now().isoformat()
            )
            
        # Process Keywords/Payloads
        for kw in iocs.get("keywords", []):
            self.add_entry(
                value=kw,
                type="keyword",
                source="github_poc",
                confidence=0.8,
                tags=["attack_vector", "payload_signature"],
                last_seen=datetime.now().isoformat()
            )

    def standardize_forecast(self):
        data = self.load_json("forecast.json")
        print(f"Processing {len(data)} Forecast entries...")
        for item in data:
            self.add_entry(
                value=item.get("cve_id"),
                type="cve",
                source="threat_forecast",
                confidence=0.5 + (item.get("trending_score", 0) / 100),
                tags=["trending", "high_risk"],
                last_seen=datetime.now().isoformat(),
                description=item.get("description", "")
            )

    def standardize_ai_insights(self):
        data = self.load_json("parsed/ai_insights.json")
        if not isinstance(data, list):
            return
            
        print(f"Processing {len(data)} AI Insight entries...")
        for entry in data:
            insights = entry.get("insights", {})
            cve_id = entry.get("cve_id", "unknown")
            
            # Add Micro-Rule
            if insights.get("micro_rule"):
                self.add_entry(
                    value=insights["micro_rule"],
                    type="micro_rule",
                    source="gemini_ai_holistic",
                    confidence=0.95,
                    tags=["active_defense", "generated_rule", "high_confidence"],
                    last_seen=datetime.now().isoformat(),
                    description=f"Holistic AI generated rule for {cve_id}"
                )
                
            # Add Target
            if insights.get("target"):
                self.add_entry(
                    value=insights["target"],
                    type="target_endpoint",
                    source="gemini_ai_holistic",
                    confidence=0.9,
                    tags=["vulnerable_endpoint"],
                    last_seen=datetime.now().isoformat(),
                    description=f"Vulnerable target in {cve_id}"
                )

            # Add Payload
            if insights.get("payload"):
                self.add_entry(
                    value=insights["payload"],
                    type="attack_payload",
                    source="gemini_ai_holistic",
                    confidence=0.9,
                    tags=["exploit_payload"],
                    last_seen=datetime.now().isoformat(),
                    description=f"Exploit payload for {cve_id}"
                )

    def run(self):
        self.standardize_reddit()
        self.standardize_cisa()
        self.standardize_poc_parser()
        self.standardize_ai_insights()
        self.standardize_forecast()
        
        output_path = os.path.join(self.data_dir, "intelligence_feed.json")
        with open(output_path, 'w') as f:
            json.dump(self.feed, f, indent=2)
        print(f"\n[+] Standardized intelligence feed saved to {output_path} with {len(self.feed)} entries.")

if __name__ == "__main__":
    std = Standardizer()
    std.run()
