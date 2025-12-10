import os
import re
import sys
from glob import glob

# Ensure we can import from utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Keywords that indicate exploit behavior
THREAT_KEYWORDS = [
    "exploit", "payload", "reverse shell", "vulnerability", "rce", "lfi", "rfi",
    "command injection", "csrf", "xss", "buffer overflow", "poc", "unauthenticated",
    "privilege escalation", "arbitrary code", "webshell", "directory traversal",
    "remote code execution", "malicious", "sqli", "file upload", "admin access"
]

def extract_ioc_from_text(text):
    found_keywords = [
        kw for kw in THREAT_KEYWORDS if re.search(rf'\b{re.escape(kw)}\b', text, re.IGNORECASE)
    ]
    return {
        "ips": list(set(re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', text))),
        "urls": list(set(re.findall(r'https?://[\w\-.:/?#@!$&()*+,;=%~]+', text))),
        "domains": list(set(re.findall(r'\b(?:[a-zA-Z0-9\-]+\.)+[a-zA-Z]{2,10}\b', text))),
        "base64": list(set(re.findall(r'\b(?:[A-Za-z0-9+/]{16,}={0,2})\b', text))),
        "keywords": list(set(found_keywords))
    }

def parse_repo_files(repo_path):
    extracted = {
        "files_parsed": [],
        "iocs": {"ips": [], "urls": [], "domains": [], "base64": [], "keywords": []},
        "ai_insights": [] # Store rich AI data here
    }

    # Scan common files used in PoCs
    patterns = [
        "*.py", "*.md"
    ]

    # Initialize AI Parser once per repo scan if possible to save init time
    ai_parser = None
    try:
        from utils.ai_parser import AIParser
        ai_parser = AIParser()
    except ImportError:
        try:
            from osint_harvester.utils.ai_parser import AIParser
            ai_parser = AIParser()
        except:
            pass

    ai_success_count = 0

    for pattern in patterns:
        for file in glob(os.path.join(repo_path, "**", pattern), recursive=True):
            extracted["files_parsed"].append(file)
            try:
                with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # AI Analysis - Limit to 1 file per repo to verify insights
                    if ai_parser and ai_parser.client and ai_success_count < 1:
                        # Only analyze code files or significant text files to save quota
                        if len(content) > 50 and len(content) < 20000: 
                            print(f"    [AI] Analyzing {os.path.basename(file)}...")
                            ai_result = ai_parser.analyze_code(content)
                            
                            if "error" not in ai_result:
                                extracted["ai_insights"].append(ai_result)
                                ai_success_count += 1
                                print(f"    [AI] Success! Insights extracted.")
                                
                                # Merge AI results into IOCs for backward compatibility
                                if ai_result.get("target"): 
                                    extracted["iocs"]["domains"].append(ai_result["target"])
                                if ai_result.get("payload"): 
                                    extracted["iocs"]["keywords"].append(ai_result["payload"])
                                if ai_result.get("attack_type"): 
                                    extracted["iocs"]["keywords"].append(ai_result["attack_type"])
                                if ai_result.get("micro_rule"):
                                    extracted["iocs"]["keywords"].append(f"RULE: {ai_result['micro_rule']}")
                            else:
                                print(f"    [AI] Error: {ai_result.get('error')}")

                    # Fallback/Complement with Regex
                    iocs = extract_ioc_from_text(content)
                    for key in iocs:
                        extracted["iocs"][key].extend(iocs[key])
            except Exception as e:
                print(f"[Warn] couldn't read {file}: {e}")



    # Remove duplicates and sort
    for key in extracted["iocs"]:
        extracted["iocs"][key] = sorted(list(set(extracted["iocs"][key])))

    return extracted

def consolidate_repo_content(repo_path, max_chars=30000):
    """
    Reads multiple files from the repo and combines them into a single text block.
    Prioritizes app.py, main.py, and README.md.
    """
    combined_text = f"Analysis of Repository: {os.path.basename(repo_path)}\n\n"
    priority_files = ["app.py", "main.py", "README.md", "server.py", "exploit.py"]
    
    # Find all relevant files
    all_files = []
    patterns = ["*.py", "*.md", "*.js", "*.txt"]
    for pattern in patterns:
        all_files.extend(glob(os.path.join(repo_path, "**", pattern), recursive=True))
        
    # Sort files: priority files first, then alphabetical
    def sort_key(f_path):
        name = os.path.basename(f_path)
        if name in priority_files:
            return (0, priority_files.index(name))
        return (1, name)
    
    all_files.sort(key=sort_key)
    
    current_chars = len(combined_text)
    
    for file_path in all_files:
        if current_chars >= max_chars:
            break
            
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                # Skip empty or very small files
                if len(content) < 10: 
                    continue
                    
                # Add file header
                file_header = f"\n\n--- FILE: {os.path.relpath(file_path, repo_path)} ---\n"
                
                # Truncate large individual files to be fair to others
                if len(content) > 5000:
                    content = content[:5000] + "\n...[TRUNCATED]..."
                
                if current_chars + len(file_header) + len(content) > max_chars:
                    # Add what fits
                    remaining = max_chars - current_chars - len(file_header)
                    if remaining > 100:
                        combined_text += file_header + content[:remaining] + "\n...[GLOBAL TRUNCATED]"
                    break
                
                combined_text += file_header + content
                current_chars += len(file_header) + len(content)
        except Exception as e:
            print(f"[Warn] Skipping {file_path}: {e}")
            
    return combined_text

def analyze_repo_holistically(repo_path):
    """
    Consolidates repo content and performs a SINGLE AI query.
    """
    print(f"    [AI] Consolidating files for holistic analysis...")
    context = consolidate_repo_content(repo_path)
    
    try:
        # Import here to avoid circular deps if any
        from utils.ai_parser import AIParser
        ai_parser = AIParser()
        
        if ai_parser.client:
            print(f"    [AI] Sending {len(context)} chars to Gemini...")
            return ai_parser.analyze_code(context)
        else:
            return {"error": "AI Client not initialized"}
    except Exception as e:
        return {"error": str(e)}
