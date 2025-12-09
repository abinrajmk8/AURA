import json
import os
try:
    from langchain_community.llms import Ollama
    from langchain.prompts import PromptTemplate
except ImportError:
    print("LangChain or Ollama not installed. Please run: pip install langchain langchain-community ollama")
    Ollama = None

class AIParser:
    def __init__(self, model="phi3"):
        # Default to phi3 as it is lightweight and CPU-friendly
        self.model_name = model
        if Ollama:
            self.llm = Ollama(model=model)
        else:
            self.llm = None

    def analyze_code(self, code_snippet):
        if not self.llm:
            return {"error": "LLM not initialized"}

        template = """
        You are a cybersecurity analyst. Analyze the following PoC code.
        Extract:
        1. Target (IP/URL/Variable)
        2. Payload (The malicious string/byte sequence)
        3. Attack Type (RCE, SQLi, etc.)

        Code:
        {code_snippet}

        Output strictly in JSON format:
        {{
          "target": "...",
          "payload": "...",
          "attack_type": "..."
        }}
        """
        
        prompt = PromptTemplate.from_template(template)
        chain = prompt | self.llm
        try:
            # Limit context to first 2000 chars to save time/memory
            result = chain.invoke({"code_snippet": code_snippet[:2000]})
            return json.loads(result)
        except Exception as e:
            return {"error": str(e)}

if __name__ == "__main__":
    # Test
    sample_code = """
    import requests
    target = "http://192.168.1.10/vuln.php"
    payload = "' OR 1=1 --"
    requests.get(target + "?id=" + payload)
    """
    parser = AIParser(model="phi3") # Use phi3, tinyllama, or qwen2:0.5b for CPU
    print(parser.analyze_code(sample_code))
