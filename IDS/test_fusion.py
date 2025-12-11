import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.fusion_engine import FusionEngine

def test_fusion():
    engine = FusionEngine()
    
    print("Testing Fusion Engine Logic...\n")
    
    # Case 1: Veto - High Confidence OSINT
    score, reason = engine.calculate_score(ids_score=0.1, osint_score=1.0)
    verdict = engine.get_verdict(score)
    print(f"Case 1 (OSINT Veto): IDS=0.1, OSINT=1.0 -> Score={score}, Verdict={verdict}")
    assert score == 1.0
    assert verdict == "BLOCK"
    
    # Case 2: Veto - High Confidence IDS
    score, reason = engine.calculate_score(ids_score=0.96, osint_score=0.0)
    verdict = engine.get_verdict(score)
    print(f"Case 2 (IDS Veto): IDS=0.96, OSINT=0.0 -> Score={score}, Verdict={verdict}")
    assert score == 1.0
    assert verdict == "BLOCK"
    
    # Case 3: Fusion - Ambiguous (Both medium)
    # Score = (0.5 * 0.6) + (0.3 * 0.5) = 0.3 + 0.15 = 0.45 -> PASS
    score, reason = engine.calculate_score(ids_score=0.6, osint_score=0.5)
    verdict = engine.get_verdict(score)
    print(f"Case 3 (Fusion Low): IDS=0.6, OSINT=0.5 -> Score={score}, Verdict={verdict}")
    assert verdict == "PASS" # 0.45 < 0.5
    
    # Case 4: Fusion - High Risk (Both high but not veto)
    # Score = (0.5 * 0.8) + (0.3 * 0.8) = 0.4 + 0.24 = 0.64 -> REDIRECT
    score, reason = engine.calculate_score(ids_score=0.8, osint_score=0.8)
    verdict = engine.get_verdict(score)
    print(f"Case 4 (Fusion High): IDS=0.8, OSINT=0.8 -> Score={score}, Verdict={verdict}")
    assert verdict == "REDIRECT"
    
    print("\n[+] All Fusion Tests Passed!")

if __name__ == "__main__":
    test_fusion()
