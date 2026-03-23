"""
YouTube adapter for fetching trending videos, comments, and search results.
Requires YouTube API v3 credentials in .env:
  YOUTUBE_API_KEY
If not configured, uses public trending data from YouTubeRSS.
"""
from adapters.base import to_unified_df
from datetime import datetime, timezone


def fetch_youtube_trending(
    max_results: int = 50,
    region_code: str = "US",
) -> tuple["pd.DataFrame | None", str | None]:
    """
    Fetch trending YouTube videos using YouTube API v3.
    Returns (DataFrame in unified schema, error_message).
    On success, error_message is None.
    """
    try:
        from dotenv import load_dotenv
        load_dotenv()
        import os

        api_key = os.getenv("YOUTUBE_API_KEY")
        if not api_key:
            return None, "YouTube API not configured. Add YOUTUBE_API_KEY to .env"
    except ImportError:
        return None, "python-dotenv required for YouTube API."

    try:
        import googleapiclient.discovery
    except ImportError:
        return None, "google-api-python-client not installed. Run: pip install google-api-python-client"

    try:
        youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)
        
        request = youtube.videos().list(
            part="snippet,statistics",
            chart="mostPopular",
            regionCode=region_code,
            maxResults=min(max_results, 50),
            fields="items(id,snippet(title,description,publishedAt,tags),statistics)"
        )
        response = request.execute()
        
        items = response.get("items", [])
        if not items:
            return None, f"No trending videos found for region {region_code}"
        
        texts = []
        timestamps = []
        for item in items:
            snippet = item.get("snippet", {})
            title = snippet.get("title", "")
            desc = snippet.get("description", "")
            text = (title + " " + desc).strip() or title
            
            published = snippet.get("publishedAt", "")
            ts = published if published else datetime.now(timezone.utc).isoformat()
            
            texts.append(text)
            timestamps.append(ts)
        
        df = to_unified_df("youtube", texts, timestamps)
        return df, None
        
    except Exception as e:
        return None, f"YouTube API error: {str(e)}"


def quick_youtube_scrape(query: str = "trending", limit: int = 30) -> tuple["pd.DataFrame | None", str | None]:
    """Scrape YouTube search results via HTML parsing (no API key needed).

    Returns (DataFrame with platform|text|timestamp, None) on success,
    (None, error_message) on failure.
    """
    try:
        import requests
    except ImportError:
        return None, "requests library not installed"

    try:
        import urllib.parse
        import re

        ua = "Mozilla/5.0 (compatible; trend-analysis-app/1.0; +https://streamlit.io)"
        search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"

        resp = requests.get(search_url, headers={"User-Agent": ua}, timeout=15)
        if resp.status_code != 200:
            return None, f"YouTube returned HTTP {resp.status_code}"
        html = resp.text

        # Try to extract video titles from the page HTML.
        titles = re.findall(r'<a[^>]+id="video-title"[^>]*title="([^"]+)"', html)
        if not titles:
            titles = re.findall(r'<a[^>]+id="video-title"[^>]*aria-label="([^"]+)"', html)

        # Also attempt to parse JSON initial data if HTML parsing fails.
        if not titles:
            js_matches = re.findall(r'"videoRenderer"\s*:\s*\{.*?"title"\s*:\s*\{.*?"text"\s*:\s*"([^"]+)"', html)
            titles = js_matches

        if not titles:
            return None, "No YouTube results found for this search query"

        rows = []
        now_ts = datetime.now(timezone.utc).isoformat()
        for title in titles[:limit]:
            text = title.strip()
            if not text:
                continue
            rows.append({"platform": "youtube", "text": text, "timestamp": now_ts})

        if not rows:
            return None, "No YouTube results extracted from the page"

        import pandas as pd
        return pd.DataFrame(rows, columns=["platform", "text", "timestamp"]), None
    except Exception as e:
        return None, str(e)
