import pandas as pd
import requests
import json
from datetime import datetime,timedelta,timezone
import os
from display_utils import display_cve_table

def fetch_cves(keyword=None ,severity=None):
   
    #______configurations____________

    end_date  = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days =7)

    #format date 
    start_str = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_str = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")

    #___________API request_________________
    url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    params = {
        "resultsPerPage" : 20,
        "pubStartDate": start_str,
        "pubEndDate": end_str

    }
    headers = {
        "User-Agent" :"CVE-Fetcher/1.0"
    }


    # fetch data 
    response = requests.get(url , headers = headers , params = params)

    if response.status_code!=200:
        print(f"[!] failed to fetch data , status code :{response.status_code}")
        print(response.text)
        exit()
    try:
        data = response.json()
    except json.JSONDecodeError:
        print("[!] failed to decode Json from response")
        print(response.text)
        exit()


    #extract cve info 
    cve_items = []

    #severity order 
    severity_order = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]


    for item in data.get("vulnerabilities", []):
        cve = item["cve"]
        description = cve["descriptions"][0]["value"]
        severity = cve.get("metrics", {}).get("cvssMetricV31", [{}])[0].get("cvssData", {}).get("baseSeverity", "N/A")
        score = cve.get("metrics", {}).get("cvssMetricV31", [{}])[0].get("cvssData", {}).get("baseScore", "N/A")

        # Apply keyword filter
        if keyword and keyword.lower() not in description.lower():
            continue

        # Apply severity filter
        if severity and severity in severity_order:
            if severity_order.index(severity) < severity_order.index(severity):
                continue

        info = {
            "id": cve["id"],
            "published": cve.get("published"),
            "lastModified": cve.get("lastModified"),
            "description": description,
            "severity": severity,
            "score": score,
            "source": "NVD"
        }
        cve_items.append(info)

    os.makedirs("data",exist_ok=True)

    # Load old data if exists
    existing = []
    json_path = "data/latest_cves.json"
    if os.path.exists(json_path):
        with open(json_path, "r") as f:
            try:
                existing = json.load(f)
            except:
                pass  # ignore broken json

    # Merge and remove duplicates by CVE ID
    all_cves = {cve["id"]: cve for cve in existing + cve_items}
    merged_cves = list(all_cves.values())

    with open(json_path, "w") as f:
        json.dump(merged_cves, f, indent=2)



    df = pd.DataFrame(merged_cves)
    df.to_csv("data/latest_cves.csv",index=False)

    display_cve_table(cve_items)
# print(f"Fetched and saved {len(cve_items)}CVEs.")