import pandas as pd
import json
import re
import numpy as np
from sklearn.linear_model import LinearRegression
from rich.console import Console
from rich.table import Table


#___load data from reddit.json____
def reddit_load():
    file_path = "./data/reddit_posts.json"
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        data = []
    return data

#___load data from github.json____
def github_load():
    file_path = "./data/github_repos.json"
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        data = []
    return data


#___calculate momentum score for trending CVEs___
# This function calculates the momentum score based on the daily counts of CVE mentions.
def momentum_score(daily_counts):
    if len(daily_counts) < 2:
        return 0.0
    
    X = np.array(range(len(daily_counts))).reshape(-1, 1)
    y = np.array(daily_counts)

    model = LinearRegression()
    model.fit(X, y)

    slope = model.coef_[0]
    return slope



#___threat forecasting function___
# This function analyzes Reddit and GitHub posts to identify trending CVEs based on mentions.
def threat_forecast():
    # --- Main Data Loading and Preparation ---
    file_path = "./data/reddit_posts.json"
    cve_list = []

    console=Console()
    table=Table(title="CVE Mentions in Reddit Posts and Github Repositories", show_lines=True)
    table.add_column("CVE ID", style="cyan", no_wrap=True)      
    table.add_column("Mentions", style="magenta")

    reddit_data = reddit_load()
    git_data = github_load()
    pattern = r"CVE-\d{4}-\d{3,7}"  # Regex pattern to match CVE IDs

    for data in reddit_data:
        title = data.get("title", "") 
        matches = re.findall(pattern, title, re.IGNORECASE)
        if matches:
            # Get the date safely, assuming it might be missing
            date = data.get("created", "unknown-date")
            date=date.split()[0]  # Convert to date format
            # Ensure we only add the first matched CVE per post to avoid duplicates from one title
            cve_list.append({"cve_id": matches[0], "date": date})
    
    for data in git_data:
        title = data.get("name", "") 
        matches = re.findall(pattern, title, re.IGNORECASE)
        if matches:
            # Get the date safely, assuming it might be missing
            date = data.get("updated", "unknown-date")
            date = date.split("T")[0]  # Convert to date format
            # Ensure we only add the first matched CVE per post to avoid duplicates from one title
            cve_list.append({"cve_id": matches[0], "date": date})

    df = pd.DataFrame(cve_list)
    # Group by both cve_id and date to get daily counts
    daily_counts_df = df.groupby(["cve_id", "date"]).size().reset_index(name='count')
    daily_counts_df = daily_counts_df.sort_values(by="date", ascending=False).reset_index(drop=True)
    # print(daily_counts_df)
    trending_scores = []
    unique_cves = daily_counts_df["cve_id"].unique()

    for cve in unique_cves:
        cve_df = daily_counts_df[daily_counts_df["cve_id"] == cve]
        cve_df = cve_df.sort_values(by="date", ascending=False)
        
        acceleration_score = 0
        
        if len(cve_df) >= 2:
            latest_mentions = cve_df.iloc[0]['count']
            second_latest_mention = cve_df.iloc[1]['count']
            acceleration_score = latest_mentions - second_latest_mention
        elif len(cve_df) == 1:
            acceleration_score = cve_df.iloc[0]['count']

        recent_counts = cve_df['count'].head(5).tolist()
        recent_counts.reverse()

        
        final_score = (0.6 * acceleration_score) + (0.4 * momentum_score(recent_counts))
        
       
        if final_score > 0:
            trending_scores.append({"cve_id": cve, "trending_score": final_score})

   
    trending_scores.sort(key=lambda x: x['trending_score'], reverse=True)

    top_threats =  trending_scores[:5] 
    # print(top_threats)
    if not daily_counts_df.empty:        
        print("🔥 Top 5 Trending CVEs:")
        for threat in top_threats:
            # print(f"  - {threat['cve_id']}: Trending Score = {threat['trending_score']:.2f}")
            table.add_row(threat['cve_id'], str(threat['trending_score']))
        console.print(table)
        return top_threats
    else:
        print("No CVEs found in the data to analyze.")

 

