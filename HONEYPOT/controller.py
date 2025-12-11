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
    
    # Default users
    users = [
        "root:0:0:root",
        "admin:1000:1000:password",
        "support:1001:1001:support"
    ]
    
    # Write to file
    try:
        with open(USERDB_PATH, "w") as f:
            for user in users:
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
