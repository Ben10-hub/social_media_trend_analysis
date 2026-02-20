"""
Multi-platform data adapters.
Unified schema: platform | text | timestamp
"""
from adapters.base import to_unified_df
from adapters.csv_adapter import load_csv_unified
from adapters.reddit_adapter import fetch_reddit_posts
from adapters.twitter_adapter import fetch_twitter_posts

__all__ = [
    "to_unified_df",
    "load_csv_unified",
    "fetch_reddit_posts",
    "fetch_twitter_posts",
]
