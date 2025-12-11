import time
import sys
from scapy.all import send, IP, TCP, UDP, Raw, RandShort

def test_osint_rule():
    print("[*] Simulating OSINT Rule Attack (CVE-2025-54253)...")
    # This payload matches the AI-generated rule: debug=OGNL:...
    payload = "GET /adminui/debug?debug=OGNL:whoami HTTP/1.1\r\nHost: target\r\n\r\n"
    
    pkt = IP(dst="127.0.0.1")/TCP(dport=80, sport=RandShort(), flags="PA")/Raw(load=payload)
    send(pkt, verbose=False)
    print("[+] Sent Malicious OGNL Payload. Check IDS for 'OSINT_BLOCK'.")

def test_ml_dos():
    print("\n[*] Simulating DoS Attack (Behavioral Anomaly)...")
    print("[*] Sending 500 packets in quick succession...")
    
    # High volume of small packets to trigger "Flow Packets/s" or "Flow IAT" anomalies
    for i in range(500):
        pkt = IP(dst="127.0.0.1")/UDP(dport=8080, sport=RandShort())/Raw(load="X"*10)
        send(pkt, verbose=False)
        if i % 100 == 0:
            sys.stdout.write(".")
            sys.stdout.flush()
            
    print("\n[+] DoS Simulation Complete. Check IDS for 'ML_ANOMALY' (Result depends on model sensitivity).")

if __name__ == "__main__":
    print("=== AURA Attack Simulator ===")
    test_osint_rule()
    time.sleep(2)
    test_ml_dos()
