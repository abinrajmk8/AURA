import joblib
import pandas as pd
import numpy as np
import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

MODEL_DIR = "IDS/models"

def test_model():
    print("[*] Loading models...")
    try:
        model = joblib.load(os.path.join(MODEL_DIR, "aura_ids_lightgbm.pkl"))
        scaler = joblib.load(os.path.join(MODEL_DIR, "scaler.pkl"))
        label_encoder = joblib.load(os.path.join(MODEL_DIR, "label_encoder.pkl"))
        print("[+] Models loaded successfully!")
        
        if hasattr(scaler, 'feature_names_in_'):
            print(f"[*] Feature Names ({len(scaler.feature_names_in_)}):")
            print(list(scaler.feature_names_in_))
        else:
            print("[-] Scaler does not store feature names.")
            
    except Exception as e:
        print(f"[-] Error loading models: {e}")
        return

    # Test Case 1: Random Noise (Likely BENIGN)
    print("\n[*] Test Case 1: Random Low-Value Input (Simulating Normal Traffic)...")
    input_benign = np.random.rand(1, 78) * 10 # Small random values
    
    try:
        scaled_benign = scaler.transform(input_benign)
        pred_benign = model.predict(scaled_benign)
        label_benign = label_encoder.inverse_transform(pred_benign)[0]
        print(f"[+] Prediction: {label_benign}")
    except Exception as e:
        print(f"[-] Error: {e}")

    # Test Case 2: Simulated Attack (High Values)
    # Attacks often have high flow duration, high packet counts, or specific port patterns
    print("\n[*] Test Case 2: Simulated High-Value Input (Simulating DoS/Attack)...")
    # Create an input with very large values for some features (like Flow Duration, Packet Count)
    input_attack = np.random.rand(1, 78) * 100000 
    # Manually spike some features to extreme values
    input_attack[0, 1] = 99999999 # Flow Duration
    input_attack[0, 2] = 50000    # Total Fwd Packets
    
    try:
        scaled_attack = scaler.transform(input_attack)
        pred_attack = model.predict(scaled_attack)
        label_attack = label_encoder.inverse_transform(pred_attack)[0]
        print(f"[+] Prediction: {label_attack}")
    except Exception as e:
        print(f"[-] Error: {e}")

if __name__ == "__main__":
    test_model()
