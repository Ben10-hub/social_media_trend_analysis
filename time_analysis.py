"""
Time-based trend analysis: hourly/minute grouping, peak activity, trend growth.
"""
import re
from collections import Counter
from datetime import datetime

import numpy as np
import pandas as pd


def parse_timestamp(ts: str | float | int) -> datetime | None:
    """Parse timestamp string or unix timestamp to datetime."""
    if pd.isna(ts):
        return None
    if isinstance(ts, (int, float)):
        try:
            return datetime.utcfromtimestamp(float(ts))
        except (ValueError, OSError):
            return None
    s = str(ts).strip()
    for fmt in [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%d",
        "%Y/%m/%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%d/%m/%Y %H:%M",
    ]:
        try:
            return datetime.strptime(s[:26].replace("Z", ""), fmt)
        except ValueError:
            continue
    try:
        return pd.to_datetime(s).to_pydatetime()
    except Exception:
        return None


def add_parsed_timestamp(df: pd.DataFrame, ts_col: str = "timestamp") -> pd.DataFrame:
    """Add _dt column with parsed datetime. Drops rows with unparseable timestamps."""
    out = df.copy()
    out["_dt"] = out[ts_col].apply(parse_timestamp)
    out = out.dropna(subset=["_dt"])
    return out


def time_group_key(dt: datetime, interval: str) -> str:
    """Return group key for interval: 'hour' or 'minute'."""
    if interval == "minute":
        return dt.strftime("%Y-%m-%d %H:%M")
    return dt.strftime("%Y-%m-%d %H:00")


def compute_trends_over_time(
    df: pd.DataFrame,
    text_col: str = "text",
    ts_col: str = "timestamp",
    interval: str = "hour",
    top_k: int = 10,
    keyword_regex: str = r"[a-zA-Z]{3,}",
) -> tuple[pd.DataFrame, pd.DataFrame, str | None]:
    """
    Compute:
      1. posts_per_interval: count of posts per time bucket
      2. keywords_per_interval: top keywords per interval
      3. peak_interval: timestamp string of peak activity
    Returns (posts_per_interval_df, keywords_per_interval_df, peak_interval_str).
    """
    out = add_parsed_timestamp(df, ts_col)
    if out.empty:
        return pd.DataFrame(), pd.DataFrame(), None

    out["_key"] = out["_dt"].apply(lambda d: time_group_key(d, interval))

    # Posts per interval
    posts_per = out.groupby("_key").size().reset_index(name="count")
    posts_per = posts_per.sort_values("_key").rename(columns={"_key": "interval"})

    # Peak
    peak_row = posts_per.loc[posts_per["count"].idxmax()]
    peak_interval = str(peak_row["interval"])

    # Keywords per interval (simple regex tokenization)
    pattern = re.compile(keyword_regex)
    keyword_counts = []
    for k, grp in out.groupby("_key"):
        texts = grp[text_col].astype(str).tolist()
        c = Counter()
        for t in texts:
            c.update(w.lower() for w in pattern.findall(t) if len(w) >= 2)
        for word, cnt in c.most_common(top_k):
            keyword_counts.append({"interval": k, "keyword": word, "count": cnt})

    kw_per = pd.DataFrame(keyword_counts) if keyword_counts else pd.DataFrame(columns=["interval", "keyword", "count"])

    return posts_per, kw_per, peak_interval


def trend_growth_rate(posts_per_interval: pd.DataFrame) -> float | None:
    """Simple growth rate: (last - first) / first if first > 0."""
    if posts_per_interval.empty or len(posts_per_interval) < 2:
        return None
    posts_per_interval = posts_per_interval.sort_values("interval")
    first = posts_per_interval["count"].iloc[0]
    last = posts_per_interval["count"].iloc[-1]
    if first <= 0:
        return None
    return (last - first) / first
