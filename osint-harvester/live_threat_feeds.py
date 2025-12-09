# import snscrape.modules.twitter as sntwitter
import praw
import requests
from datetime import datetime , timezone
from dotenv import load_dotenv
load_dotenv()
import os



    
#_____________________Reddit Feed ________________

def fetch_reddit( subreddit = "netsec",keyword = "CVE",limit = 10):
    if not os.getenv("REDDIT_CLIENT_ID") or not os.getenv("REDDIT_CLIENT_SECRET"):
        print("[!] Reddit credentials not found in .env. Skipping Reddit fetch.")
        return []

    try:
        reddit = praw.Reddit(
                client_id=os.getenv("REDDIT_CLIENT_ID"),
                client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
                user_agent=os.getenv("REDDIT_USER_AGENT", "AURA_OSINT_BOT")
            )
        posts = []
        for post in reddit.subreddit(subreddit).search(keyword,limit=limit):
            posts.append({
                "title":post.title,
                "url":post.url,
                "score":post.score,
                "created":datetime.fromtimestamp(post.created_utc, tz=timezone.utc).strftime('%Y-%m-%d %H:%M')
            })
        return posts
    except Exception as e:
        print(f"[!] Error fetching Reddit: {e}")
        return []
    
#___________________github PoC  search ________________________

def fetch_github(keyword="CVE-2025",limit = 10):
    headers = {"Accept" : "application/vnd.github+json"}
    url = f"https://api.github.com/search/repositories?q={keyword}+exploit+PoC+in:name,description+language:Python&sort=updated&per_page={limit}"
    response = requests.get(url , headers = headers)
    results = []
    for item in response.json().get("items",[]):
        results.append({
            "name":item.get("full_name"),
            "url":item.get("html_url"),
            "updated":item.get("updated_at")
        })
    return results

#______________________CISA KEV API+______________________________

def fetch_cisa():
    url = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("vulnerabilities",[])
    return []
#__________________Twitter or X _____________---   not working now , (may be later )

# def fetch_x(keyword = "CVE-2025" , limit = 10):
#     query = f"{keyword} exploit"
#     tweets = []
#     for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
#         if i >= limit:
#             break
#         tweets.append({
#             "date":tweet.date.strftime("%Y-%m-%d %H:%M"),
#             "user" :tweet.user.username,
#             "content":tweet.content,
#             "url":tweet.url
#         })
#         return tweets

