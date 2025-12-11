import os
import subprocess
import json
import joblib
import re
import numpy as np
import pandas as pd
import warnings
from rich.console import Console
from .flow_generator import FlowGenerator

# Suppress sklearn/lightgbm warnings about feature names
warnings.filterwarnings("ignore", message=".*X does not have valid feature names.*")

console = Console()

class Detector:
    def __init__(self, model_dir="IDS/models", feed_path="data/intelligence_feed.json"):
        self.flow_gen = FlowGenerator()
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.osint_data = {
            "ips": set(),
            "urls": set(),
            "rules": []
        }
        
        self.load_models(model_dir)
        self.load_osint(feed_path)
        
    def load_models(self, model_dir):
        try:
            self.model = joblib.load(os.path.join(model_dir, "aura_ids_lightgbm.pkl"))
            self.scaler = joblib.load(os.path.join(model_dir, "scaler.pkl"))
            self.label_encoder = joblib.load(os.path.join(model_dir, "label_encoder.pkl"))
            console.print("[bold green][+] ML Models loaded successfully.[/bold green]")
        except Exception as e:
            console.print(f"[bold red][-] Error loading ML models: {e}[/bold red]")

    def load_osint(self, feed_path):
        if not os.path.exists(feed_path):
            console.print(f"[yellow][!] OSINT feed not found at {feed_path}. Running without OSINT.[/yellow]")
            return
            
        try:
            with open(feed_path, 'r') as f:
                feed = json.load(f)
                
            for entry in feed:
                val = entry.get("value", "")
                type_ = entry.get("type", "")
                
                if type_ == "ipv4":
                    self.osint_data["ips"].add(val)
                elif type_ == "micro_rule":
                    try:
                        # Compile regex for speed
                        self.osint_data["rules"].append({
                            "pattern": re.compile(val, re.IGNORECASE),
                            "desc": entry.get("description", "Unknown Rule")
                        })
                    except re.error:
                        pass
                        
            console.print(f"[bold green][+] OSINT Feed loaded: {len(self.osint_data['ips'])} IPs, {len(self.osint_data['rules'])} Rules.[/bold green]")
        except Exception as e:
            console.print(f"[bold red][-] Error loading OSINT feed: {e}[/bold red]")

    def check_osint(self, packet):
        """Layer 1: Fast Check against known IOCs"""
        if not packet.haslayer('IP'):
            return None
            
        src_ip = packet['IP'].src
        
        # 1. IP Reputation
        if src_ip in self.osint_data["ips"]:
            return f"OSINT_BLOCK: Malicious IP {src_ip}"
            
        # 2. Payload Rules (Deep Packet Inspection)
        if packet.haslayer('Raw'):
            payload = packet['Raw'].load.decode('utf-8', errors='ignore')
            for rule in self.osint_data["rules"]:
                if rule["pattern"].search(payload):
                    return f"OSINT_BLOCK: Rule Match - {rule['desc']}"
                    
        return None

    def block_ip(self, ip_address):
        """Executes active blocking via iptables (IPS Mode)."""
        if ip_address == "127.0.0.1":
            console.print(f"[bold yellow][SAFETY] Would block {ip_address}, but skipping localhost safety check.[/bold yellow]")
            return

        try:
            # Check if rule already exists to avoid duplicates
            check_cmd = f"sudo iptables -C INPUT -s {ip_address} -j DROP"
            if subprocess.call(check_cmd.split(), stderr=subprocess.DEVNULL) == 0:
                return # Rule exists

            cmd = f"sudo iptables -A INPUT -s {ip_address} -j DROP"
            subprocess.run(cmd.split(), check=True)
            console.print(f"[bold red][IPS] 🛡️  Active Block Executed for {ip_address}[/bold red]")
        except Exception as e:
            console.print(f"[red]Failed to block IP: {e}[/red]")

    def process_packet(self, packet):
        """Main Pipeline: Packet -> OSINT -> Flow -> ML"""
        
        src_ip = packet['IP'].src if packet.haslayer('IP') else None

        # Step 1: OSINT Check
        osint_verdict = self.check_osint(packet)
        if osint_verdict:
            if src_ip: self.block_ip(src_ip)
            return {"action": "BLOCK", "reason": osint_verdict}
            
        # Step 2: Flow Processing
        flow_key = self.flow_gen.process_packet(packet)
        if not flow_key:
            return None # Not an IP packet or ignored
            
        # Step 3: ML Check (Triggered periodically or on flow finish)
        # For real-time, we check every N packets or if flow is long enough
        # Here we check immediately for demonstration
        features = self.flow_gen.extract_features(flow_key)
        
        if features and self.model:
            try:
                # Reshape for model (1 sample, 78 features)
                input_vec = np.array(features).reshape(1, -1)
                scaled_vec = self.scaler.transform(input_vec)
                prediction = self.model.predict(scaled_vec)
                
                # Decode label
                label = "UNKNOWN"
                if hasattr(self.label_encoder, 'inverse_transform'):
                    label = self.label_encoder.inverse_transform(prediction)[0]
                else:
                    label = prediction[0]
                    
                if label == "ATTACK":
                    # For ML anomalies, we might want to alert first, or block if confidence is high.
                    # For this demo, we will block.
                    if src_ip: self.block_ip(src_ip)
                    return {"action": "ALERT", "reason": f"ML_ANOMALY: Behavioral Detection"}
                    
            except Exception as e:
                # console.print(f"[red]ML Error: {e}[/red]")
                pass
                
        return {"action": "PASS", "reason": "Clean"}
