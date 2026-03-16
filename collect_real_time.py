import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv(override=True)

def collect_reddit_data(search_query="technology", limit=10):
    """Fetches real-time posts from Reddit using RapidAPI Reddit3."""
    url = "https://reddit3.p.rapidapi.com/v1/reddit/search"
    
    headers = {
        "x-rapidapi-key": os.getenv('RAPIDAPI_KEY'),
        "x-rapidapi-host": "reddit3.p.rapidapi.com"
    }
    
    params = {
        "search": search_query,
        "filter": "posts",
        "sortType": "relevance",
        "timeFilter": "all"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            # Reddit3 uses the 'results' key for post lists
            posts = data.get('results', [])
            
            # Format for your existing dataframe structure
            return [{"platform": "reddit", "text": p.get('title')} for p in posts[:limit]]
        return []
    except Exception as e:
        print(f"Reddit Error: {e}")
        return []