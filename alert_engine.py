"""
Keyword spike detection utilities.

Goal: detect sudden spikes in keyword frequency vs a rolling baseline, using
hourly buckets derived from df['timestamp'] and tokens from df['text'].
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from datetime import datetime

import pandas as pd


WORD_RE = re.compile(r"[A-Za-z]{2,}")


def _safe_parse_dt(x) -> datetime | None:
    if x is None or pd.isna(x):
        return None
    if isinstance(x, datetime):
        return x
    s = str(x).strip()
    if not s:
        return None
    try:
        # pandas is fairly robust for mixed timestamp formats.
        return pd.to_datetime(s, errors="coerce").to_pydatetime()
    except Exception:
        return None


def _hour_bucket(dt: datetime) -> pd.Timestamp:
    # Use pandas Timestamp for easy sorting/printing.
    ts = pd.Timestamp(dt)
    return ts.floor("h")


def _tokenize(text: str) -> list[str]:
    if not isinstance(text, str):
        return []
    return [w.lower() for w in WORD_RE.findall(text)]


def detect_keyword_spikes(df: pd.DataFrame, window: int = 5, spike_multiplier: float = 2.0):
    """
    Detect keyword spikes relative to a rolling average over past `window` hours.

    Input:
      df: DataFrame with at least columns: text, timestamp
    Returns:
      list of dicts: [{keyword, current_count, avg_count, spike_ratio, timestamp}]
    """
    if df is None or df.empty:
        return []
    if "text" not in df.columns or "timestamp" not in df.columns:
        return []
    if window < 1:
        window = 1
    try:
        spike_multiplier = float(spike_multiplier)
    except Exception:
        spike_multiplier = 2.0

    # Build hourly keyword counts.
    hour_to_counter: dict[pd.Timestamp, Counter] = defaultdict(Counter)
    try:
        for _, r in df[["text", "timestamp"]].iterrows():
            dt = _safe_parse_dt(r["timestamp"])
            if dt is None:
                continue
            hour = _hour_bucket(dt)
            tokens = _tokenize(r["text"] if isinstance(r["text"], str) else str(r["text"]))
            if not tokens:
                continue
            hour_to_counter[hour].update(tokens)
    except Exception:
        return []

    if not hour_to_counter:
        return []

    hours = sorted(hour_to_counter.keys())
    spikes: list[dict] = []

    # For each hour, compare each keyword count to rolling avg from previous hours.
    for i, h in enumerate(hours):
        current = hour_to_counter[h]
        if not current:
            continue
        prev_hours = hours[max(0, i - window) : i]
        if not prev_hours:
            continue

        # Compute rolling average counts per keyword from previous intervals.
        baseline_sum: Counter = Counter()
        for ph in prev_hours:
            baseline_sum.update(hour_to_counter[ph])
        denom = max(1, len(prev_hours))

        for kw, cur_cnt in current.items():
            if cur_cnt <= 0:
                continue
            avg = baseline_sum.get(kw, 0) / denom
            if avg <= 0:
                continue
            ratio = cur_cnt / avg if avg > 0 else None
            if ratio is not None and ratio > spike_multiplier:
                spikes.append(
                    {
                        "keyword": kw,
                        "current_count": int(cur_cnt),
                        "avg_count": float(avg),
                        "spike_ratio": float(ratio),
                        "timestamp": h.isoformat(),
                    }
                )

    # Sort: newest spikes first, then biggest ratios.
    try:
        spikes.sort(key=lambda d: (d.get("timestamp", ""), d.get("spike_ratio", 0.0)), reverse=True)
    except Exception:
        pass
    return spikes


def get_alert_summary(spikes) -> str:
    """Return a human-readable summary string for a list returned by detect_keyword_spikes()."""
    if not spikes:
        return "No unusual keyword spikes detected."
    lines: list[str] = []
    for s in spikes[:25]:
        try:
            kw = s.get("keyword")
            ratio = float(s.get("spike_ratio", 0.0))
            ts = s.get("timestamp", "")
            lines.append(f"'{kw}' spiked {ratio:.1f}x above average (hour: {ts})")
        except Exception:
            continue
    return "\n".join(lines) if lines else "Keyword spikes detected."

