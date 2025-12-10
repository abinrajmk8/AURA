import os
import json
import shutil
from .cloner import clone_repo
from .parser import parse_repo_files, analyze_repo_holistically
from .feed_loader import load_repos_from_feed  
from rich.console import Console

console = Console()

REPO_DIR = "cloned_repos"
OUTPUT_FILE = "./data/parsed/refined_poc.json"

def handle_remove_readonly(func, path, exc):
    import stat
    os.chmod(path, stat.S_IWRITE)
    func(path)

def run_github_poc_parser(repo_list, limit=None):
    results = []
    ai_insights_results = []

    # Apply limit if provided
    if limit:
        repo_list = repo_list[:limit]

    for i, item in enumerate(repo_list):
        cve_id = item["cve"]
        url = item["repo_url"]
        dest = os.path.join(REPO_DIR, cve_id)

        console.print(f"\n🔍 Processing [bold red] {cve_id} [/bold red] from [bold green]{url}[/bold green]")
        if clone_repo(url, dest):
            # 1. Standard Regex Parsing (No AI calls inside here anymore if we removed them, or we just ignore them)
            # Actually, we should probably disable the per-file AI call in parser.py or just let it fail/skip.
            # But the user asked to "add this using python program... and generate ai insight seperately".
            parse_data = parse_repo_files(dest)
            results.append({
                "cve_id": cve_id,
                "repo": url,
                **parse_data
            })
            
            # 2. Holistic AI Analysis (Only for the first one to be safe, or all if limit is small)
            # User said "just pass one repo... generate ai insight seperately"
            if i == 0: 
                ai_data = analyze_repo_holistically(dest)
                if "error" not in ai_data:
                    ai_insights_results.append({
                        "cve_id": cve_id,
                        "repo": url,
                        "insights": ai_data
                    })
                else:
                    console.print(f"[bold red][!] AI Analysis Failed: {ai_data['error']}[/bold red]")

            shutil.rmtree(dest, onerror=handle_remove_readonly)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2)
        
    # Save AI Insights separately
    if ai_insights_results:
        ai_file = "./data/parsed/ai_insights.json"
        with open(ai_file, 'w') as f:
            json.dump(ai_insights_results, f, indent=2)
        console.print(f"[bold green][+] AI Insights saved to: {ai_file}[/bold green]")

    # Fully remove cloned_repos even if some folders are readonly or locked
    if os.path.exists(REPO_DIR):
        shutil.rmtree(REPO_DIR, onerror=handle_remove_readonly)

    console.print(f"\n[bold green][+]\t\tParsing completed.[/bold green]\t Output saved to: {OUTPUT_FILE}")
    return results
