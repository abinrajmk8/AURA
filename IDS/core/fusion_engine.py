import logging

class FusionEngine:
    """
    Fusion Engine: The decision-making core of AURA.
    Combines inputs from IDS (ML), OSINT (Intel), and Trend Analysis to calculate a Final Threat Score.
    
    Logic:
    1. Veto Power: If any single source is 100% confident (or near it), it overrides others.
    2. Weighted Fusion: For ambiguous cases, a weighted average is used.
    """
    
    def __init__(self):
        # Weights for the fusion formula
        self.w_ids = 0.5
        self.w_osint = 0.3
        self.w_trend = 0.2
        
        # Thresholds
        self.threshold_block = 0.8
        self.threshold_redirect = 0.5
        
    def calculate_score(self, ids_score, osint_score, trend_score=0.0):
        """
        Calculates the Final Threat Score (0.0 - 1.0).
        """
        
        # --- VETO LOGIC (Overrides) ---
        
        # 1. OSINT Veto: Known Malicious IP or Rule Match
        if osint_score >= 1.0:
            return 1.0, "BLOCK (OSINT Veto)"
            
        # 2. IDS Veto: High Confidence ML Detection
        if ids_score > 0.95:
            return 1.0, "BLOCK (IDS Veto)"
            
        # --- WEIGHTED FUSION (Ambiguous Cases) ---
        
        final_score = (self.w_ids * ids_score) + \
                      (self.w_osint * osint_score) + \
                      (self.w_trend * trend_score)
                      
        # Cap score at 1.0
        final_score = min(final_score, 1.0)
        
        reason = f"Fusion Score: {final_score:.2f} (IDS:{ids_score:.2f}, OSINT:{osint_score:.2f})"
        return final_score, reason

    def get_verdict(self, final_score):
        """
        Returns the action based on the score.
        """
        if final_score >= self.threshold_block:
            return "BLOCK"
        elif final_score >= self.threshold_redirect:
            return "REDIRECT" # In practice, this might log as ALERT or route to Honeypot
        else:
            return "PASS"
