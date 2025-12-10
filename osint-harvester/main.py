# main.py
import argparse
import json
import csv
import os
import sys
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Import existing modules
from cve_fetcher import fetch_cves
from live_threat_feeds import fetch_reddit, fetch_github, fetch_cisa
from github_poc_parser.run_parser import run_github_poc_parser
from github_poc_parser.feed_loader import load_repos_from_feed
from correlator import correlate_pocs_with_feeds
from threat_forecaster import threat_forecast
from utils.standardizer import Standardizer

console = Console()
title = Text()
title.append("AURA", style="bold red")
title.append(" OSINT HARVESTER", style="bold blue")

def save_json_with_merge(new_data, path, unique_key):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    existing = []
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            try:
                existing = json.load(f)
            except json.JSONDecodeError:
                pass

    all_items = {item[unique_key]: item for item in existing + new_data if unique_key in item}
    merged = list(all_items.values())

    with open(path, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2)

def main():
    parser = argparse.ArgumentParser(description="Fetch and filter CVEs, optionally parse PoCs or fetch live OSINT feeds")
    # Removed --mode argument as this is now purely harvester
    parser.add_argument("--keyword", type=str, help="Keyword to filter by (e.g. wordpress, iot, sql)")
    parser.add_argument("--severity", type=str, choices=["LOW", "MEDIUM", "HIGH", "CRITICAL"], help="Minimum severity level")
    parser.add_argument("--live", action="store_true", help="Include Reddit, GitHub, and CISA live threat feeds")
    parser.add_argument("--poc", action="store_true", help="Parse GitHub PoC repos from data/github_repos.json")
    parser.add_argument("--correlate", action="store_true", help="Correlate parsed PoCs with CISA/NVD feeds")
    parser.add_argument("--forecast", action="store_true", help="Run threat forecasting based on Reddit posts")
    args = parser.parse_args()

    console.print(Panel.fit(title, border_style="bright_magenta", padding=(1, 4)))

    # Harvest Mode Logic
    # Run CVE fetcher
    fetch_cves(args.keyword, args.severity)

    # Optional: fetch live OSINT feeds
    if args.live:
        console.print("\n[bold green][+][/bold green] [bold blue] Reddit [/bold blue]/r/netsec Posts:")
        reddit_posts = fetch_reddit(keyword=args.keyword or "CVE")
        for p in reddit_posts[:5]:
            print(f"- {p['created']} | {p['title']}")

        console.print("\n[bold green][+][/bold green] [bold blue] GitHub CVE PoCs: [/bold blue]")
        github_repos = fetch_github(keyword=args.keyword or "CVE", limit=5)
        for g in github_repos:
            print(f"- {g['updated']} | {g['name']} | {g['url']}")

        console.print("\n[bold green][+][/bold green] [bold blue]  CISA KEV Listings: [/bold blue] ")
        cisa_vulns = fetch_cisa()[:3]
        for v in cisa_vulns:
            print(f"- {v['cveID']} | {v['vendorProject']} | {v['vulnerabilityName']}")

        # Save JSONs
        save_json_with_merge(reddit_posts, "data/reddit_posts.json", unique_key="url")
        save_json_with_merge(github_repos, "data/github_repos.json", unique_key="url")
        save_json_with_merge(cisa_vulns, "data/cisa_vulns.json", unique_key="cveID")

        # CSV generation removed as requested

        if args.forecast:
            console.print("\n[bold green][+][/bold green] Running threat forecasting...")
            threat_forecasts=threat_forecast()
            save_json_with_merge(threat_forecasts, "data/forecast.json", unique_key="cve_id")

    # Optional: run GitHub PoC parser
    if args.poc:
        console.print("\n[bold green][+][/bold green] Running GitHub PoC parser (Limit: 1 repo due to rate limits)...")
        repo_list = load_repos_from_feed("data/github_repos.json")
        run_github_poc_parser(repo_list, limit=1)

    if args.correlate:
        correlate_pocs_with_feeds(
            poc_path="data/parsed/poc_output.json",
            cisa_path="data/cisa_vulns.json",
            nvd_path="data/latest_cves.json",
            output_path="./data/parsed/correlated_output.json"
        )
    
    # Always run standardization at the end if any data was fetched
    console.print("\n[bold green][+][/bold green] Standardizing Intelligence Feed...")
    std = Standardizer()
    std.run()

if __name__ == "__main__":
    main()
