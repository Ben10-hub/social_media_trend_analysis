"""
Twitter/X adapter using Tweepy.
Requires Twitter API v2 credentials in .env:
  TWITTER_BEARER_TOKEN  (or API key/secret for v1)
If not configured, returns None with fallback message.
"""
from adapters.base import to_unified_df


def fetch_twitter_posts(
    query: str = "trending",
    max_results: int = 50,
) -> tuple["pd.DataFrame | None", str | None]:
    """
    Fetch tweets. Returns (DataFrame in unified schema, error_message).
    On success, error_message is None.
    If Tweepy/credentials missing, returns (None, "fallback message").
    """
    try:
        from dotenv import load_dotenv

        load_dotenv()
        import os

        bearer = os.getenv("TWITTER_BEARER_TOKEN")
        if not bearer:
            return None, "Twitter API not configured. Add TWITTER_BEARER_TOKEN to .env (API v2)"
    except ImportError:
        return None, "python-dotenv required for Twitter. Use sample dataset or Reddit instead."

    try:
        import tweepy
    except ImportError:
        return None, "Tweepy not installed. Run: pip install tweepy. Use sample dataset or Reddit instead."

    try:
        client = tweepy.Client(bearer_token=bearer)
        response = client.search_recent_tweets(
            query=query,
            max_results=min(max_results, 100),
            tweet_fields=["created_at", "text"],
            user_fields=[],
            expansions=[],
        )
    except Exception as e:
        return None, f"Twitter API error: {str(e)}"

    if not response.data:
        return None, "No tweets returned. Try a different query or check API limits."

    import datetime as dt

    texts = [t.text for t in response.data]
    timestamps = [t.created_at.isoformat() if t.created_at else dt.datetime.utcnow().isoformat() for t in response.data]
    df = to_unified_df("twitter", texts, timestamps)
    return df, None
