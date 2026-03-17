"""
CSV adapter: loads uploaded or sample CSV into unified schema.
"""
import io
from pathlib import Path

import pandas as pd

# Preferred text columns (order matters)
TEXT_COLS = ["text", "clean_text", "clean_comment", "comment", "content", "body", "post", "tweet", "message"]
# Preferred timestamp columns
TS_COLS = ["timestamp", "created_at", "date", "datetime", "time", "posted_at"]
# Platform column if present
PLATFORM_COLS = ["platform", "source", "channel"]
# Location columns (optional)
LOCATION_COLS = ["location", "country", "region", "city"]


def infer_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    for c in candidates:
        if c in df.columns:
            return c
    for col in df.columns:
        cl = col.lower()
        for cand in candidates:
            if cand.lower() in cl:
                return col
    return None


def load_csv_unified(
    file_bytes: bytes | None = None,
    file_path: str | Path | None = None,
    platform_default: str = "csv",
) -> pd.DataFrame:
    """
    Load CSV from bytes or file path, convert to unified schema.
    Returns DataFrame with columns: platform | text | timestamp | (optional) location
    """
    if file_bytes is not None:
        df = pd.read_csv(io.BytesIO(file_bytes))
    elif file_path is not None:
        df = pd.read_csv(Path(file_path))
    else:
        raise ValueError("Provide file_bytes or file_path")

    text_col = infer_column(df, TEXT_COLS)
    if text_col is None:
        raise ValueError("CSV must have a text-like column (text, clean_text, clean_comment, etc.)")

    ts_col = infer_column(df, TS_COLS)
    platform_col = infer_column(df, PLATFORM_COLS)
    loc_col = infer_column(df, LOCATION_COLS)

    n = len(df)
    texts = df[text_col].astype(str).tolist()
    if ts_col:
        timestamps = df[ts_col].astype(str).tolist()
        if len(timestamps) != n:
            timestamps = [pd.Timestamp.utcnow().isoformat()] * n
    else:
        timestamps = [pd.Timestamp.utcnow().isoformat()] * n
    if platform_col:
        platforms = df[platform_col].astype(str).tolist()
        if len(platforms) != n:
            platforms = [platform_default] * n
    else:
        platforms = [platform_default] * n

    out = pd.DataFrame({"text": texts, "timestamp": timestamps, "platform": platforms})
    if loc_col:
        try:
            locs = df[loc_col].astype(str).replace({"nan": ""}).tolist()
        except Exception:
            locs = [""] * n
        out["location"] = [s.strip() or None for s in locs]
        return out[["platform", "text", "timestamp", "location"]]
    return out[["platform", "text", "timestamp"]]
