# correlator.py

import json
import os
from rich.console import Console

console = Console()

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def correlate_pocs_with_feeds(poc_path, cisa_path, nvd_path, output_path):
    pocs = load_json(poc_path)
    cisa_entries = {item["cveID"]: item for item in load_json(cisa_path)}
    nvd_entries = {item["id"]: item for item in load_json(nvd_path)}

    enriched = []
    for poc in pocs:
        cve_id = poc["cve_id"]

        # Merge all data
        correlated = {
            **poc,
            "cisa": cisa_entries.get(cve_id, {}),
            "nvd": nvd_entries.get(cve_id, {})
        }

        enriched.append(correlated)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(enriched, f, indent=2)

    console.print(f"\n[bold green][+]\t\tCorrelation complete.[/bold green]\t  Output saved to : {output_path}\n")
    return enriched
