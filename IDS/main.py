import argparse
import sys
import os
from scapy.all import sniff, conf
from rich.console import Console
from rich.table import Table
from rich.live import Live

# Ensure we can import core modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.detector import Detector

console = Console()

def get_default_iface():
    """Attempts to find a suitable default interface."""
    # Simple heuristic: look for common names
    for iface in conf.ifaces.values():
        if iface.name in ['eth0', 'wlan0', 'en0', 'Wi-Fi']:
            return iface.name
    return conf.iface # Scapy default

def main():
    parser = argparse.ArgumentParser(description="AURA IDS - Real-time Hybrid Intrusion Detection System")
    parser.add_argument("-i", "--interface", help="Network interface to sniff on (e.g., eth0, wlan0)")
    parser.add_argument("--pcap", help="Read from PCAP file instead of live capture")
    args = parser.parse_args()

    # Initialize Detector
    console.print("[bold blue][*] Initializing AURA IDS Engine...[/bold blue]")
    detector = Detector()
    
    iface = args.interface if args.interface else get_default_iface()
    console.print(f"[bold blue][*] Starting Sniffer on interface: [green]{iface}[/green][/bold blue]")
    console.print("[bold yellow]Press Ctrl+C to stop.[/bold yellow]\n")

    # Stats counters
    stats = {"processed": 0, "blocks": 0, "alerts": 0}

    def packet_callback(packet):
        stats["processed"] += 1
        
        # Run Detection
        result = detector.process_packet(packet)
        
        if result:
            action = result["action"]
            reason = result["reason"]
            
            if action == "BLOCK":
                stats["blocks"] += 1
                console.print(f"[bold red]🛑 BLOCKED | {reason} | Src: {packet[0][1].src if packet.haslayer('IP') else '?'}[/bold red]")
            elif action == "ALERT":
                stats["alerts"] += 1
                console.print(f"[bold orange]⚠️  ALERT   | {reason} | Src: {packet[0][1].src if packet.haslayer('IP') else '?'}[/bold orange]")
            # else: PASS (Silent)
            
        # Periodic status update (every 100 packets)
        if stats["processed"] % 100 == 0:
            print(f"\r[*] Processed: {stats['processed']} | Blocks: {stats['blocks']} | Alerts: {stats['alerts']}", end="")

    try:
        if args.pcap:
            sniff(offline=args.pcap, prn=packet_callback, store=0)
        else:
            sniff(iface=iface, prn=packet_callback, store=0)
    except KeyboardInterrupt:
        console.print("\n[bold blue][*] IDS Stopped.[/bold blue]")
    except Exception as e:
        console.print(f"\n[bold red][!] Sniffer Error: {e}[/bold red]")

if __name__ == "__main__":
    main()
