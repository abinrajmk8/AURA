#!/usr/bin/env python3
"""
controller.py
Manages Honeypot configuration based on AURA Intelligence.
"""

import sys
import os
import time
from pathlib import Path

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from database.db_manager import DBManager

# New path for the simplified setup
USERDB_PATH = Path.cwd() / "HONEYPOT/userdb.txt"

db = DBManager()

def update_userdb():
    """Fetch credentials from OSINT rules and update userdb.txt."""
    print("[*] Updating Honeypot Credentials from Intelligence Feed...")
    
    # Base credentials (always present)
    users = {
        "root:0:0:root",
        "admin:1000:1000:password",
        "support:1001:1001:support",
        "user:1002:1002:123456"
    }
    
    # Keyword to Credential Mapping
    # If OSINT feed contains these keywords/tags, add these credentials
    bait_map = {
        "iot": ["admin:1003:1003:admin", "root:0:0:12345"],
        "router": ["admin:1003:1003:admin", "cisco:1004:1004:cisco"],
        "camera": ["admin:1003:1003:12345", "service:1005:1005:service"],
        "d-link": ["admin:1003:1003:admin"],
        "hikvision": ["admin:1003:1003:12345"],
        "realtek": ["realtek:1006:1006:realtek"],
        "ssh": ["test:1007:1007:test", "guest:1008:1008:guest"]
    }
    
    feed_path = Path.cwd() / "data/intelligence_feed.json"
    
    if feed_path.exists():
        try:
            import json
            with open(feed_path, 'r') as f:
                feed = json.load(f)
                
            # Scan feed for keywords
            active_keywords = set()
            for entry in feed:
                # Check tags
                for tag in entry.get("tags", []):
                    tag_lower = tag.lower()
                    for keyword in bait_map:
                        if keyword in tag_lower:
                            active_keywords.add(keyword)
                            
                # Check description/value
                text = (entry.get("description", "") + " " + entry.get("value", "")).lower()
                for keyword in bait_map:
                    if keyword in text:
                        active_keywords.add(keyword)
            
            # Add bait credentials
            for keyword in active_keywords:
                print(f"[+] Found active threat keyword: {keyword}. Adding bait credentials.")
                for cred in bait_map[keyword]:
                    users.add(cred)
                    
        except Exception as e:
            print(f"[!] Error reading intelligence feed: {e}")
    else:
        print(f"[!] Intelligence feed not found at {feed_path}")

    # Write to file
    try:
        with open(USERDB_PATH, "w") as f:
            for user in sorted(list(users)):
                f.write(user + "\n")
        
        print(f"[+] Updated {USERDB_PATH} with {len(users)} users.")
        
    except Exception as e:
        print(f"[!] Error updating userdb: {e}")

def main():
    print("[+] AURA Honeypot Controller Started")
    
    while True:
        update_userdb()
        # Sleep for 1 hour (simulated)
        print("[*] Sleeping for 60 seconds...")
        time.sleep(60)

if __name__ == "__main__":
    main()
