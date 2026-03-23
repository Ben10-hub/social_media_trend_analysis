"""
Global Trends Module - Fetches real-time trending topics from multiple sources
Combines trends from Reddit, Twitter, YouTube, Instagram, and other platforms
"""
import pandas as pd
from datetime import datetime, timezone
from collections import Counter


def collect_global_trending(
    include_reddit: bool = True,
    include_twitter: bool = True,
    include_youtube: bool = True,
    include_instagram: bool = True,
    posts_per_source: int = 50,
) -> tuple[pd.DataFrame, dict]:
    """
    Collect trending posts from multiple sources simultaneously.
    Returns (combined_df, trending_topics_dict)
    """
    import warnings
    warnings.filterwarnings("ignore")
    
    all_dfs = []
    trending_topics = {}
    errors = {}
    
    # Reddit trending
    if include_reddit:
        try:
            from adapters.reddit_adapter import fetch_reddit_posts
            rdf, err = fetch_reddit_posts(
                subreddits=["worldnews", "technology", "news"],
                limit_per_sub=min(posts_per_source // 3, 50)
            )
            if rdf is not None and not rdf.empty:
                all_dfs.append(rdf)
                trending_topics["reddit"] = extract_top_keywords(rdf, top_k=10)
            elif err:
                errors["reddit"] = err
        except Exception as e:
            errors["reddit"] = str(e)
    
    # Twitter/X trending
    if include_twitter:
        try:
            from adapters.twitter_adapter import fetch_twitter_posts
            tdf, err = fetch_twitter_posts(query="trending OR viral", max_results=posts_per_source)
            if tdf is not None and not tdf.empty:
                all_dfs.append(tdf)
                trending_topics["twitter"] = extract_top_keywords(tdf, top_k=10)
            elif err:
                errors["twitter"] = err
        except Exception as e:
            errors["twitter"] = str(e)
    
    # YouTube trending
    if include_youtube:
        try:
            from adapters.youtube_adapter import quick_youtube_scrape
            ydf, err = quick_youtube_scrape(query="trending", limit=posts_per_source)
            if ydf is not None and not ydf.empty:
                all_dfs.append(ydf)
                trending_topics["youtube"] = extract_top_keywords(ydf, top_k=10)
            elif err:
                errors["youtube"] = err
        except Exception as e:
            errors["youtube"] = str(e)
    
    # Instagram trending
    if include_instagram:
        try:
            from adapters.instagram_adapter import quick_instagram_scrape
            idf, err = quick_instagram_scrape(hashtag="trending", limit=posts_per_source)
            if idf is not None and not idf.empty:
                all_dfs.append(idf)
                trending_topics["instagram"] = extract_top_keywords(idf, top_k=10)
            elif err:
                errors["instagram"] = err
        except Exception as e:
            errors["instagram"] = str(e)
    
    # Combine all dataframes
    if all_dfs:
        combined_df = pd.concat(all_dfs, ignore_index=True)
        combined_trending = extract_top_keywords(combined_df, top_k=15)
        trending_topics["global"] = combined_trending
    else:
        combined_df = pd.DataFrame(columns=["platform", "text", "timestamp"])
        combined_trending = []
    
    return combined_df, {
        "sources": trending_topics,
        "errors": errors,
        "total_posts": len(combined_df),
        "platforms": list(combined_df["platform"].unique()) if not combined_df.empty else [],
    }


def extract_top_keywords(df: pd.DataFrame, top_k: int = 10) -> list[str]:
    """Extract top keywords from a dataframe."""
    try:
        if df is None or df.empty or "text" not in df.columns:
            return []
        
        import re
        from nltk.corpus import stopwords
        from nltk.stemming import WordNetLemmatizer
        
        try:
            stop = set(stopwords.words("english"))
            lemmatizer = WordNetLemmatizer()
        except:
            stop = set()
            lemmatizer = None
        
        keywords = Counter()
        
        for text in df["text"].dropna():
            # Clean and tokenize
            text = str(text).lower()
            # Remove URLs
            text = re.sub(r"https?://\S+", "", text)
            # Remove mentions
            text = re.sub(r"@\w+", "", text)
            # Extract words
            words = re.findall(r"\b[a-z]{3,}\b", text)
            
            for word in words:
                if stop and word not in stop:
                    if lemmatizer:
                        word = lemmatizer.lemmatize(word)
                    keywords[word] += 1
                elif not stop:
                    keywords[word] += 1
        
        return [kw for kw, _ in keywords.most_common(top_k)]
    except:
        return []


def get_recent_by_platform(df: pd.DataFrame, platform: str, limit: int = 20) -> pd.DataFrame:
    """Get recent posts from a specific platform."""
    if df is None or df.empty:
        return pd.DataFrame()
    
    filtered = df[df["platform"] == platform].copy() if "platform" in df.columns else df.copy()
    
    # Sort by timestamp if available
    if "timestamp" in filtered.columns:
        try:
            filtered["_ts"] = pd.to_datetime(filtered["timestamp"], errors="coerce")
            filtered = filtered.sort_values("_ts", ascending=False).drop("_ts", axis=1)
        except:
            pass
    
    return filtered.head(limit)


def get_trending_summary(df: pd.DataFrame) -> dict:
    """Generate a summary of trending topics."""
    if df is None or df.empty:
        return {
            "total_posts": 0,
            "platforms": [],
            "top_keywords": [],
            "time_range": "N/A",
        }
    
    keywords = extract_top_keywords(df, top_k=20)
    
    # Time range
    time_range = "N/A"
    if "timestamp" in df.columns:
        try:
            df["_dt"] = pd.to_datetime(df["timestamp"], errors="coerce")
            if not df["_dt"].isna().all():
                min_time = df["_dt"].min()
                max_time = df["_dt"].max()
                if min_time and max_time:
                    delta = max_time - min_time
                    if delta.total_seconds() < 300:
                        time_range = "Last 5 minutes"
                    elif delta.total_seconds() < 3600:
                        time_range = f"Last {int(delta.total_seconds() / 60)} minutes"
                    else:
                        time_range = f"Last {int(delta.total_seconds() / 3600)} hours"
        except:
            pass
    
    return {
        "total_posts": len(df),
        "platforms": list(df["platform"].unique()) if "platform" in df.columns else [],
        "top_keywords": keywords,
        "time_range": time_range,
    }
