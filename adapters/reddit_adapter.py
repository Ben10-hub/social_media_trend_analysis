"""
Reddit adapter using PRAW.
Requires Reddit API credentials in .env:
  REDDIT_CLIENT_ID
  REDDIT_CLIENT_SECRET
  REDDIT_USER_AGENT
"""
from adapters.base import to_unified_df


def _get_reddit_client():
    """Lazy load PRAW; returns None if credentials missing or import fails."""
    try:
        from dotenv import load_dotenv

        load_dotenv()
        import os

        client_id = os.getenv("REDDIT_CLIENT_ID")
        client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        user_agent = os.getenv("REDDIT_USER_AGENT", "TrendSentimentApp/1.0")
        if not client_id or not client_secret:
            return None
        import praw

        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
        )
        return reddit
    except ImportError:
        return None
    except Exception:
        return None


def fetch_reddit_posts(
    subreddits: list[str] | None = None,
    limit_per_sub: int = 25,
) -> tuple["pd.DataFrame | None", str | None]:
    """
    Fetch posts from Reddit. Returns (DataFrame in unified schema, error_message).
    On success, error_message is None.
    """
    import pandas as pd

    if subreddits is None:
        subreddits = ["python", "technology", "worldnews"]

    reddit = _get_reddit_client()
    if reddit is None:
        return None, "Reddit API not configured. Add REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT to .env"

    texts = []
    timestamps = []
    locations = []
    try:
        for sub in subreddits[:5]:  # cap at 5 subreddits
            try:
                subreddit = reddit.subreddit(sub)
                for post in subreddit.new(limit=min(limit_per_sub, 100)):
                    texts.append(post.selftext or post.title or "")
                    timestamps.append(post.created_utc)
                    # Location is optional; use best-effort hints:
                    # - author flair text (often contains region/country)
                    # - subreddit name as a proxy location
                    loc = None
                    try:
                        flair = getattr(post, "author_flair_text", None)
                        if flair:
                            s = str(flair).strip()
                            if s and s.lower() not in {"none", "n/a", "na"}:
                                loc = s
                    except Exception:
                        loc = None
                    if not loc:
                        try:
                            sr = getattr(post, "subreddit", None)
                            sname = getattr(sr, "display_name", None) if sr is not None else None
                            if sname:
                                loc = str(sname).strip() or None
                        except Exception:
                            loc = None
                    locations.append(loc)
            except Exception as e:
                continue  # skip failed subreddit
    except Exception as e:
        return None, f"Reddit fetch error: {str(e)}"

    if not texts:
        return None, "No Reddit posts fetched. Try different subreddits or check API limits."

    import datetime as dt

    ts_str = [
        dt.datetime.utcfromtimestamp(float(t)).isoformat() if t else dt.datetime.utcnow().isoformat()
        for t in timestamps
    ]
    df = to_unified_df("reddit", texts, ts_str)
    try:
        if len(locations) == len(df):
            df["location"] = locations
    except Exception:
        pass
    return df, None
