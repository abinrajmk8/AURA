import os
import re
from glob import glob

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
        "iocs": {"ips": [], "urls": [], "domains": [], "base64": [], "keywords": []}
    }

    # Scan common files used in PoCs
    patterns = [
        "*.py", "*.sh", "*.c", "*.cpp", "*.js", "*.json", "*.xml",
        "*.conf", "*.cfg", "*.env", "*.txt", "*.md", "*.log"
    ]

    for pattern in patterns:
        for file in glob(os.path.join(repo_path, "**", pattern), recursive=True):
            extracted["files_parsed"].append(file)
            try:
                with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Try AI Analysis first (if available)
                    try:
                        from utils.ai_parser import AIParser
                        ai_parser = AIParser()
                        if ai_parser.llm:
                            print(f"    [AI] Analyzing {os.path.basename(file)}...")
                            ai_result = ai_parser.analyze_code(content)
                            if "error" not in ai_result:
                                # Merge AI results into IOCs
                                if ai_result.get("target"): extracted["iocs"]["domains"].append(ai_result["target"])
                                if ai_result.get("payload"): extracted["iocs"]["keywords"].append(ai_result["payload"])
                                if ai_result.get("attack_type"): extracted["iocs"]["keywords"].append(ai_result["attack_type"])
                    except ImportError:
                        pass
                    except Exception as e:
                        print(f"    [AI] Failed: {e}")

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
