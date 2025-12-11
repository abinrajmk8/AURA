#!/usr/bin/env python3
"""
Test IDS Service - Runs without sudo for testing
This simulates the IDS running and writing to a log file
"""
import time
import sys
import os
from datetime import datetime

print("[*] AURA IDS Test Service Started")
print(f"[*] PID: {os.getpid()}")
print("[*] Running in test mode (no sudo required)")
print("[*] Press Ctrl+C to stop\n")

# Create a log file
log_file = "dashboard/api/status/ids_test.log"

try:
    with open(log_file, 'a') as f:
        f.write(f"\n=== IDS Started at {datetime.now()} ===\n")
    
    counter = 0
    while True:
        counter += 1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"[{timestamp}] IDS Running - Packet #{counter} processed"
        
        print(message)
        
        # Write to log file
        with open(log_file, 'a') as f:
            f.write(message + "\n")
        
        time.sleep(5)  # Check every 5 seconds
        
except KeyboardInterrupt:
    print("\n[*] IDS Test Service Stopped")
    with open(log_file, 'a') as f:
        f.write(f"=== IDS Stopped at {datetime.now()} ===\n")
    sys.exit(0)
