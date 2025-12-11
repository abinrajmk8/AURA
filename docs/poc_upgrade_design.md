# AI-Enhanced PoC Analysis & RAG Design

## 1. The Problem with Regex
The current `parser.py` uses Regular Expressions. While fast, it lacks **context**.
*   It cannot distinguish between a *target IP* (victim) and a *listener IP* (attacker).
*   It cannot understand complex logic (e.g., "The payload is generated in function X but sent in function Y").
*   It misses obfuscated keywords.

## 2. Proposed Solution: LLM-Based Extraction + RAG
We will upgrade the OSINT module to use a **Local LLM** (Large Language Model) to "read" the code and a **Vector Database** to store the knowledge.

### A. Architecture
1.  **Ingestion**: Fetch PoC repositories (as done now).
2.  **Analysis (The "Brain")**:
    *   Pass the code (README, main script) to a Local LLM (e.g., Mistral/Llama3 via Ollama).
    *   **Prompt**: "Analyze this Python script. Extract the Target IP variable, the Payload structure, and the Attack Vector. Return as JSON."
3.  **Storage (The "Memory")**:
    *   Store the structured JSON in your `intelligence_feed.json`.
    *   Store the *embeddings* of the PoC text in a **Vector Database** (ChromaDB).
4.  **Retrieval (RAG)**:
    *   The IDS or Analyst can query: "Show me all PoCs that use Log4j payloads."
    *   The system retrieves relevant code snippets from ChromaDB.

### B. Technology Stack
*   **LLM Runtime**: [Ollama](https://ollama.com/) (Easy to run local models like `mistral` or `llama3`).
*   **Orchestration**: [LangChain](https://python.langchain.com/) (To manage prompts and JSON parsing).
*   **Vector DB**: [ChromaDB](https://www.trychroma.com/) (Local, open-source, file-based).

## 3. Implementation Steps

### Step 1: Setup Environment
Install necessary libraries:
```bash
pip install langchain langchain-community chromadb ollama
```
*Requirement*: You need to install [Ollama](https://ollama.com/download) on your machine and run `ollama pull mistral`.

### Step 2: Create `ai_parser.py`
This script will replace the regex logic.

```python
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
import json

llm = Ollama(model="mistral")

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

def analyze_code_with_llm(code):
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm
    result = chain.invoke({"code_snippet": code[:2000]}) # Limit context
    return json.loads(result)
```

### Step 3: Build the Knowledge Base (RAG)
Store the analyzed data.

```python
import chromadb

client = chromadb.PersistentClient(path="./data/chroma_db")
collection = client.get_or_create_collection(name="poc_knowledge")

def store_poc(cve_id, code, analysis):
    collection.add(
        documents=[code],
        metadatas=[analysis],
        ids=[cve_id]
    )
```

## 4. Benefits
*   **High Precision**: The LLM understands "target = args.ip" means `args.ip` is the target.
*   **Queryable**: You can ask questions to your dataset.
*   **Future-Proof**: Ready for "Autonomous Response" where the AI generates a patch or a specific firewall rule based on the PoC logic.

## Recommendation
Since `ids_module` is high priority, I suggest:
1.  **Phase 1 (Now)**: Stick to Regex but standardize the output (Quick fix).
2.  **Phase 2 (Parallel)**: Set up Ollama and build this `ai_parser.py` as a background task.
