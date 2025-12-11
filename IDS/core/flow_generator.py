import numpy as np
import pandas as pd
import time
from collections import deque

class FlowGenerator:
    def __init__(self):
        self.active_flows = {}  # Key: (src_ip, src_port, dst_ip, dst_port, proto)
        self.finished_flows = []
        
    def get_flow_key(self, packet):
        """Creates a unique key for the flow (bidirectional)."""
        if not packet.haslayer('IP'):
            return None
            
        src_ip = packet['IP'].src
        dst_ip = packet['IP'].dst
        proto = packet['IP'].proto
        
        src_port = 0
        dst_port = 0
        
        if packet.haslayer('TCP'):
            src_port = packet['TCP'].sport
            dst_port = packet['TCP'].dport
        elif packet.haslayer('UDP'):
            src_port = packet['UDP'].sport
            dst_port = packet['UDP'].dport
            
        # Canonical key (smaller IP first) to handle bidirectional flows
        if src_ip < dst_ip:
            return (src_ip, src_port, dst_ip, dst_port, proto)
        else:
            return (dst_ip, dst_port, src_ip, src_port, proto)

    def process_packet(self, packet):
        """Ingests a packet and updates the corresponding flow."""
        key = self.get_flow_key(packet)
        if not key:
            return None
            
        timestamp = time.time()
        
        if key not in self.active_flows:
            self.active_flows[key] = {
                'start_time': timestamp,
                'last_time': timestamp,
                'packets': [],
                'fwd_packets': 0,
                'bwd_packets': 0,
                'fwd_bytes': 0,
                'bwd_bytes': 0,
                # ... (We need to track many more stats for 78 features)
                # For simplicity in this MVP, we will calculate complex stats 
                # only when extracting features to keep ingestion fast.
            }
            
        flow = self.active_flows[key]
        flow['last_time'] = timestamp
        # Calculate Header Length (IP + TCP/UDP)
        header_len = 0
        if packet.haslayer('IP'):
            header_len += packet['IP'].ihl * 4
        if packet.haslayer('TCP'):
            header_len += packet['TCP'].dataofs * 4
        elif packet.haslayer('UDP'):
            header_len += 8
            
        # Capture Window Size
        win_size = 0
        if packet.haslayer('TCP'):
            win_size = packet['TCP'].window

        flow['packets'].append({
            'ts': timestamp,
            'len': len(packet),
            'dir': 'fwd' if packet['IP'].src == key[0] else 'bwd',
            'flags': packet['TCP'].flags if packet.haslayer('TCP') else 0,
            'header_len': header_len,
            'win': win_size
        })
        
        # Basic counters
        if packet['IP'].src == key[0]:
            flow['fwd_packets'] += 1
            flow['fwd_bytes'] += len(packet)
        else:
            flow['bwd_packets'] += 1
            flow['bwd_bytes'] += len(packet)
            
        return key

    def extract_features(self, flow_key):
        """Calculates the 78 features for a specific flow."""
        if flow_key not in self.active_flows:
            return None
            
        flow = self.active_flows[flow_key]
        packets = flow['packets']
        
        # Basic Time Stats
        duration = flow['last_time'] - flow['start_time']
        if duration == 0: duration = 1e-6 # Avoid division by zero
        
        # Packet Lengths
        lens = [p['len'] for p in packets]
        fwd_lens = [p['len'] for p in packets if p['dir'] == 'fwd']
        bwd_lens = [p['len'] for p in packets if p['dir'] == 'bwd']
        
        # Inter-Arrival Times (IAT)
        timestamps = [p['ts'] for p in packets]
        iats = np.diff(timestamps) if len(timestamps) > 1 else [0]
        
        fwd_ts = [p['ts'] for p in packets if p['dir'] == 'fwd']
        fwd_iats = np.diff(fwd_ts) if len(fwd_ts) > 1 else [0]
        
        bwd_ts = [p['ts'] for p in packets if p['dir'] == 'bwd']
        bwd_iats = np.diff(bwd_ts) if len(bwd_ts) > 1 else [0]

        # Flags (TCP)
        # Scapy flags: F, S, R, P, A, U, E, C
        flags = [p['flags'] for p in packets]
        
        def count_flag(flag_char):
            count = 0
            for f in flags:
                # Scapy flags can be FlagValue object or int
                if isinstance(f, int):
                    # Map char to bit mask if needed, but Scapy often returns objects that str() to 'PA' etc.
                    # For simplicity in this hybrid object/int world:
                    pass 
                
                # Convert to string representation for easy checking
                f_str = str(f)
                if flag_char in f_str:
                    count += 1
            return count

        # Header Lengths
        # We stored 'header_len' in process_packet now
        fwd_header_len = sum(p['header_len'] for p in packets if p['dir'] == 'fwd')
        bwd_header_len = sum(p['header_len'] for p in packets if p['dir'] == 'bwd')
        
        # Window Sizes (Initial)
        init_win_fwd = 0
        init_win_bwd = 0
        
        # Find first fwd packet with TCP layer
        for p in packets:
            if p['dir'] == 'fwd' and 'win' in p:
                init_win_fwd = p['win']
                break
                
        for p in packets:
            if p['dir'] == 'bwd' and 'win' in p:
                init_win_bwd = p['win']
                break

        # Construct the 78-feature vector (Order MUST match model)
        features = {
            'Destination Port': flow_key[3],
            'Flow Duration': duration * 1e6, # Microseconds
            'Total Fwd Packets': len(fwd_lens),
            'Total Backward Packets': len(bwd_lens),
            'Total Length of Fwd Packets': sum(fwd_lens),
            'Total Length of Bwd Packets': sum(bwd_lens),
            'Fwd Packet Length Max': max(fwd_lens) if fwd_lens else 0,
            'Fwd Packet Length Min': min(fwd_lens) if fwd_lens else 0,
            'Fwd Packet Length Mean': np.mean(fwd_lens) if fwd_lens else 0,
            'Fwd Packet Length Std': np.std(fwd_lens) if fwd_lens else 0,
            'Bwd Packet Length Max': max(bwd_lens) if bwd_lens else 0,
            'Bwd Packet Length Min': min(bwd_lens) if bwd_lens else 0,
            'Bwd Packet Length Mean': np.mean(bwd_lens) if bwd_lens else 0,
            'Bwd Packet Length Std': np.std(bwd_lens) if bwd_lens else 0,
            'Flow Bytes/s': sum(lens) / duration,
            'Flow Packets/s': len(lens) / duration,
            'Flow IAT Mean': np.mean(iats),
            'Flow IAT Std': np.std(iats),
            'Flow IAT Max': np.max(iats) if len(iats) > 0 else 0,
            'Flow IAT Min': np.min(iats) if len(iats) > 0 else 0,
            'Fwd IAT Total': sum(fwd_iats),
            'Fwd IAT Mean': np.mean(fwd_iats),
            'Fwd IAT Std': np.std(fwd_iats),
            'Fwd IAT Max': np.max(fwd_iats) if len(fwd_iats) > 0 else 0,
            'Fwd IAT Min': np.min(fwd_iats) if len(fwd_iats) > 0 else 0,
            'Bwd IAT Total': sum(bwd_iats),
            'Bwd IAT Mean': np.mean(bwd_iats),
            'Bwd IAT Std': np.std(bwd_iats),
            'Bwd IAT Max': np.max(bwd_iats) if len(bwd_iats) > 0 else 0,
            'Bwd IAT Min': np.min(bwd_iats) if len(bwd_iats) > 0 else 0,
            'Fwd PSH Flags': count_flag('P'), 
            'Bwd PSH Flags': 0, # Usually dataset only counts fwd PSH? Keeping 0 to match typical CIC flow
            'Fwd URG Flags': count_flag('U'),
            'Bwd URG Flags': 0,
            'Fwd Header Length': fwd_header_len,
            'Bwd Header Length': bwd_header_len,
            'Fwd Packets/s': len(fwd_lens) / duration,
            'Bwd Packets/s': len(bwd_lens) / duration,
            'Min Packet Length': min(lens) if lens else 0,
            'Max Packet Length': max(lens) if lens else 0,
            'Packet Length Mean': np.mean(lens) if lens else 0,
            'Packet Length Std': np.std(lens) if lens else 0,
            'Packet Length Variance': np.var(lens) if lens else 0,
            'FIN Flag Count': count_flag('F'),
            'SYN Flag Count': count_flag('S'),
            'RST Flag Count': count_flag('R'),
            'PSH Flag Count': count_flag('P'),
            'ACK Flag Count': count_flag('A'),
            'URG Flag Count': count_flag('U'),
            'CWE Flag Count': count_flag('C'),
            'ECE Flag Count': count_flag('E'),
            'Down/Up Ratio': len(bwd_lens)/len(fwd_lens) if len(fwd_lens) > 0 else 0,
            'Average Packet Size': np.mean(lens) if lens else 0,
            'Avg Fwd Segment Size': np.mean(fwd_lens) if fwd_lens else 0,
            'Avg Bwd Segment Size': np.mean(bwd_lens) if bwd_lens else 0,
            'Fwd Header Length.1': fwd_header_len, # Duplicate in dataset
            'Fwd Avg Bytes/Bulk': 0,
            'Fwd Avg Packets/Bulk': 0,
            'Fwd Avg Bulk Rate': 0,
            'Bwd Avg Bytes/Bulk': 0,
            'Bwd Avg Packets/Bulk': 0,
            'Bwd Avg Bulk Rate': 0,
            'Subflow Fwd Packets': len(fwd_lens),
            'Subflow Fwd Bytes': sum(fwd_lens),
            'Subflow Bwd Packets': len(bwd_lens),
            'Subflow Bwd Bytes': sum(bwd_lens),
            'Init_Win_bytes_forward': init_win_fwd,
            'Init_Win_bytes_backward': init_win_bwd,
            'act_data_pkt_fwd': len([l for l in fwd_lens if l > 0]),
            'min_seg_size_forward': 20, # Default TCP header size
            'Active Mean': 0, 
            'Active Std': 0,
            'Active Max': 0,
            'Active Min': 0,
            'Idle Mean': 0,
            'Idle Std': 0,
            'Idle Max': 0,
            'Idle Min': 0
        }
        
        # Return as list in correct order
        return list(features.values())
