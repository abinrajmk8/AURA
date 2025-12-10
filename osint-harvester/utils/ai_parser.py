import json
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

class AIParser:
    def __init__(self, model_name="gemini-2.5-flash"):
        # The new client automatically looks for GEMINI_API_KEY
        # But we support GEMINI_API from your .env too
        api_key = os.getenv("GEMINI_API") or os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            print("[!] GEMINI_API key not found in .env")
            self.client = None
            return
            
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def analyze_code(self, code_snippet):
        if not self.client:
            return {"error": "Gemini Client not initialized"}

        prompt = f"""
        You are a cybersecurity analyst. Analyze the following PoC code or threat description.
        Extract:
        1. Target (IP/URL/Variable)
        2. Payload (The malicious string/byte sequence)
        3. Attack Type (RCE, SQLi, etc.)
        4. Micro-Rule (A regex or snort-like signature to block this)

        Code/Description:
        {code_snippet[:8000]}

        Output strictly in JSON format:
        {{
          "target": "...",
          "payload": "...",
          "attack_type": "...",
          "micro_rule": "..."
        }}
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name, 
                contents=prompt
            )
            # Clean markdown code blocks if present
            text = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except Exception as e:
            print(f"[!] Gemini Analysis Error: {e}")
            return {"error": str(e)}

    def generate_embedding(self, text):
        # Note: The new SDK might have a different way to call embeddings.
        # For now, we are focusing on the analyze_code part as requested.
        # If needed, we would use client.models.embed_content(...)
        return []

if __name__ == "__main__":
    # Test
    sample_code = """
    import requests
    target = "http://192.168.1.10/vuln.php"
    payload = "' OR 1=1 --"
    requests.get(target + "?id=" + payload)
    """
    parser = AIParser()
    if parser.client:
        print("Analyzing sample code...")
        analysis = parser.analyze_code(sample_code)
        print("Analysis:", json.dumps(analysis, indent=2))
    else:
        print("Skipping test, no API key.")
