"""
Base adapter and unified schema utilities.
Unified schema: platform | text | timestamp
"""
import pandas as pd


def to_unified_df(platform: str, texts: list[str], timestamps: list | None = None) -> pd.DataFrame:
    """
    Build a DataFrame in unified schema: platform | text | timestamp.
    If timestamps is None, uses current time for all rows.
    """
    import datetime as dt

    n = len(texts)
    if timestamps is None or len(timestamps) != n:
        now = dt.datetime.utcnow().isoformat()
        timestamps = [now] * n
    else:
        timestamps = [str(ts) for ts in timestamps]
    return pd.DataFrame({
        "platform": [platform] * n,
        "text": [str(t) for t in texts],
        "timestamp": timestamps,
    })
