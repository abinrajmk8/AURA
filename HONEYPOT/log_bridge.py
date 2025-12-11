#!/usr/bin/env python3
"""
log_bridge.py
Bridges Cowrie JSON logs to AURA Database.
"""

import json
import time
import sys
import os
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from database.db_manager import DBManager

# New path for the simplified setup
COWRIE_JSON = Path.cwd() / "HONEYPOT/log/cowrie.json"

# Status file path
STATUS_DIR = Path("dashboard/api/status")
STATUS_FILE = STATUS_DIR / "honeypot.json"

db = DBManager()

def update_status(enabled, pid=None):
    """Update Honeypot status file"""
    STATUS_DIR.mkdir(parents=True, exist_ok=True)
    
    status = {
        "enabled": enabled,
        "status": "active" if enabled else "inactive",
        "pid": pid if enabled else None,
        "last_started": datetime.now().isoformat() if enabled else None,
        "last_stopped": None if enabled else datetime.now().isoformat(),
        "uptime": "0s"
    }
    
    with open(STATUS_FILE, 'w') as f:
        json.dump(status, f, indent=2)

def process_event(event):
    """Log interesting events to DB."""
    event_id = event.get("eventid")
    src_ip = event.get("src_ip")
    if not src_ip: return

    alert_type = "HONEYPOT_MISC"
    severity = "LOW"
    desc = event.get("message", "Unknown Event")
    payload = ""
    action = "MONITORED"

    if event_id == "cowrie.login.success":
        alert_type = "HONEYPOT_BREACH"
        severity = "CRITICAL"
        desc = f"Attacker logged in as {event.get('username')}/{event.get('password')}"
    elif event_id == "cowrie.login.failed":
        alert_type = "HONEYPOT_AUTH"
        severity = "MEDIUM"
        desc = f"Failed login: {event.get('username')}/{event.get('password')}"
    elif event_id == "cowrie.command.input":
        alert_type = "HONEYPOT_CMD"
        severity = "HIGH"
        payload = event.get("input")
        desc = f"Attacker executed: {payload}"
    elif event_id == "cowrie.session.file_download":
        alert_type = "HONEYPOT_DOWNLOAD"
        severity = "HIGH"
        payload = event.get("url")
        desc = f"Malware download: {payload}"
    
    # Only log interesting events
    if alert_type != "HONEYPOT_MISC":
        db.log_alert(src_ip, alert_type, desc, payload, action)
        print(f"[+] Logged {alert_type} from {src_ip}")

def tail_file(path):
    """Tail the file and yield new lines."""
    with path.open("r", encoding="utf-8", errors="ignore") as fh:
        fh.seek(0, 2)  # go to end
        while True:
            line = fh.readline()
            if not line:
                time.sleep(0.5)
                continue
            yield line

def main():
    if not COWRIE_JSON.exists():
        print(f"[!] Cowrie JSON not found at {COWRIE_JSON}")
        return

    # Update status to enabled on startup
    pid = os.getpid()
    update_status(enabled=True, pid=pid)
    print(f"[+] Honeypot Status: ENABLED (PID: {pid})")

    print(f"[+] Watching {COWRIE_JSON} -> AURA Database")
    
    try:
        for rawline in tail_file(COWRIE_JSON):
            rawline = rawline.strip()
            if not rawline: continue
            try:
                event = json.loads(rawline)
                process_event(event)
            except json.JSONDecodeError:
                continue
    except KeyboardInterrupt:
        print("\n[*] Honeypot Stopped.")
    finally:
        # Update status to disabled on shutdown
        update_status(enabled=False)
        print("[*] Honeypot Status: DISABLED")

if __name__ == "__main__":
    main()
