import json
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import sys

# Ensure we can import from utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from utils.ai_parser import AIParser
except ImportError:
    # Fallback
    from osint_harvester.utils.ai_parser import AIParser

class ThreatCorrelator:
    def __init__(self, feed_path="./data/intelligence_feed.json"):
        self.feed_path = feed_path
        self.knowledge_base = []
        self.embeddings = []
        # Initialize AI Parser (it will load API key from env)
        self.ai = AIParser()
        self.load_knowledge_base()

    def load_knowledge_base(self):
        if not os.path.exists(self.feed_path):
            print(f"[!] Knowledge base not found at {self.feed_path}")
            return

        with open(self.feed_path, 'r') as f:
            try:
                self.knowledge_base = json.load(f)
                # Extract embeddings into a numpy array for fast search
                self.embeddings = []
                self.valid_indices = []
                
                print("[*] Loading Knowledge Base Embeddings...")
                for i, entry in enumerate(self.knowledge_base):
                    emb = entry.get("embedding")
                    if emb and len(emb) > 0:
                        self.embeddings.append(emb)
                        self.valid_indices.append(i)
                
                if self.embeddings:
                    self.embeddings = np.array(self.embeddings)
                    print(f"[+] Loaded {len(self.embeddings)} embeddings into Knowledge Base.")
                else:
                    print("[!] No embeddings found in Knowledge Base.")
                    
            except Exception as e:
                print(f"[!] Error loading knowledge base: {e}")

    def correlate(self, alert_text):
        """
        Correlates an IDS alert text with the knowledge base.
        Returns: (best_match_entry, score)
        """
        if len(self.embeddings) == 0:
            return None, 0.0

        # Generate embedding for the alert
        alert_embedding = self.ai.generate_embedding(alert_text)
        if not alert_embedding:
            return None, 0.0

        # Reshape for sklearn (1, -1)
        alert_embedding = np.array(alert_embedding).reshape(1, -1)
        
        # Calculate similarities
        # self.embeddings is (N, D), alert is (1, D)
        similarities = cosine_similarity(alert_embedding, self.embeddings)
        
        # Get best match
        best_idx_in_embeddings = np.argmax(similarities)
        best_score = similarities[0][best_idx_in_embeddings]
        
        # Map back to original knowledge base index
        original_idx = self.valid_indices[best_idx_in_embeddings]
        best_match = self.knowledge_base[original_idx]
        
        return best_match, float(best_score)

if __name__ == "__main__":
    # Test
    correlator = ThreatCorrelator(feed_path="../data/intelligence_feed.json")
    if correlator.embeddings is not None and len(correlator.embeddings) > 0:
        test_alert = "Detected suspicious LDAP request with jndi payload"
        match, score = correlator.correlate(test_alert)
        print(f"Alert: {test_alert}")
        print(f"Match: {match.get('value')} (Score: {score:.4f})")
