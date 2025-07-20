import os
import json
import shutil
from .cloner import clone_repo
from .parser import parse_repo_files
from .feed_loader import load_repos_from_feed  
from rich.console import Console

console = Console()

REPO_DIR = "cloned_repos"
OUTPUT_FILE = "./data/parsed/poc_output.json"

def handle_remove_readonly(func, path, exc):
    import stat
    os.chmod(path, stat.S_IWRITE)
    func(path)

def run_github_poc_parser(repo_list):
    results = []

    for item in repo_list:
        cve_id = item["cve"]
        url = item["repo_url"]
        dest = os.path.join(REPO_DIR, cve_id)

        console.print(f"\n🔍 Processing [bold red] {cve_id} [/bold red] from [bold green]{url}[/bold green]")
        if clone_repo(url, dest):
            parse_data = parse_repo_files(dest)
            results.append({
                "cve_id": cve_id,
                "repo": url,
                **parse_data
            })
            shutil.rmtree(dest, onerror=handle_remove_readonly)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2)

    # Fully remove cloned_repos even if some folders are readonly or locked
    shutil.rmtree(REPO_DIR, onerror=handle_remove_readonly)

    console.print(f"\n[bold green][+]\t\tParsing completed.[/bold green]\t Output saved to: {OUTPUT_FILE}")
    return results
