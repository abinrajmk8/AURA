import time
import random
import numpy as np
import joblib
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from IDS.core.fusion_engine import FusionEngine

def benchmark_fusion_engine(n_iterations=50000):
    print(f"[*] Benchmarking Fusion Engine ({n_iterations} iterations)...")
    engine = FusionEngine()
    
    start_time = time.time()
    for _ in range(n_iterations):
        ids_score = random.random()
        osint_score = random.random()
        engine.calculate_score(ids_score, osint_score)
    end_time = time.time()
    
    duration = end_time - start_time
    ops_per_sec = n_iterations / duration
    print(f"    -> Duration: {duration:.4f}s")
    print(f"    -> Throughput: {ops_per_sec:.2f} decisions/sec")
    return ops_per_sec

def benchmark_model_inference(model_path, n_samples=1000):
    print(f"\n[*] Benchmarking ML Model Inference ({n_samples} samples)...")
    
    if not os.path.exists(model_path):
        print(f"    [!] Model file not found at {model_path}")
        return
        
    try:
        model = joblib.load(model_path)
        # Generate dummy features (78 features as per notebook)
        dummy_input = np.random.rand(n_samples, 78)
        
        start_time = time.time()
        model.predict(dummy_input)
        end_time = time.time()
        
        duration = end_time - start_time
        latency_per_sample = (duration / n_samples) * 1000 # ms
        throughput = n_samples / duration
        
        print(f"    -> Duration: {duration:.4f}s")
        print(f"    -> Average Latency: {latency_per_sample:.4f} ms/sample")
        print(f"    -> Throughput: {throughput:.2f} predictions/sec")
        
    except Exception as e:
        print(f"    [!] Error loading/running model: {e}")

def benchmark_system_simulation(n_cycles=1000):
    print(f"\n[*] Benchmarking System Logic Simulation ({n_cycles} cycles)...")
    # Simulate: Packet -> Feature Ext -> Fusion -> Decision
    
    engine = FusionEngine()
    
    start_time = time.time()
    for _ in range(n_cycles):
        # 1. Feature Extraction (Simulated)
        _ = np.random.rand(78)
        
        # 2. Fusion
        ids_score = random.random()
        osint_score = random.random()
        engine.calculate_score(ids_score, osint_score)
        
    end_time = time.time()
    duration = end_time - start_time
    pps = n_cycles / duration
    
    print(f"    -> Duration: {duration:.4f}s")
    print(f"    -> Estimated Logic Throughput: {pps:.2f} cycles/sec")

if __name__ == "__main__":
    print("=== AURA System Performance Benchmark ===\n")
    
    benchmark_fusion_engine()
    
    model_path = os.path.join(os.path.dirname(__file__), "models", "aura_ids_lightgbm.pkl")
    benchmark_model_inference(model_path)
    
    benchmark_system_simulation()
    
    print("\n=== End Benchmark ===")
