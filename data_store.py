"""
Local storage for collected posts: SQLite with append and dedup.
Unified schema: platform | text | timestamp
"""
import os
import sqlite3
from pathlib import Path

import pandas as pd

_PROJECT_DIR = Path(__file__).resolve().parent
_DB_PATH = _PROJECT_DIR / "data" / "social_data.db"


def _ensure_db() -> None:
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(_DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT,
                text TEXT,
                timestamp TEXT,
                location TEXT,
                UNIQUE(platform, text)
            )
            """
        )
        # Backward-compatible migration: older DBs may not have location column.
        try:
            cols = [r[1] for r in conn.execute("PRAGMA table_info(posts)").fetchall()]
            if "location" not in cols:
                conn.execute("ALTER TABLE posts ADD COLUMN location TEXT")
        except Exception:
            # If migration fails for any reason, keep app functional without location.
            pass


def get_db_path() -> str:
    """Return path to SQLite database for user reference."""
    _ensure_db()
    return str(_DB_PATH)


def append_posts(df: pd.DataFrame, dedup: bool = True) -> tuple[int, str | None]:
    """
    Append posts to SQLite. Returns (number_added, error_message).
    If dedup=True, skips rows with same (platform, text).
    """
    if df is None or df.empty:
        return 0, None
    req = {"platform", "text", "timestamp"}
    if not req.issubset(df.columns):
        return 0, "DataFrame must have columns: platform, text, timestamp"
    _ensure_db()
    df = df.copy()
    if "location" not in df.columns:
        df["location"] = None
    df = df[["platform", "text", "timestamp", "location"]].copy()
    df = df.dropna(subset=["text"])
    df["text"] = df["text"].astype(str).str.strip()
    df = df[df["text"].str.len() > 0]
    if df.empty:
        return 0, None
    rows = [
        (
            r["platform"],
            r["text"],
            str(r["timestamp"]),
            (None if pd.isna(r["location"]) else str(r["location"]).strip() or None),
        )
        for _, r in df.iterrows()
    ]
    try:
        with sqlite3.connect(_DB_PATH) as conn:
            before = conn.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
            if dedup:
                conn.executemany(
                    "INSERT OR IGNORE INTO posts (platform, text, timestamp, location) VALUES (?, ?, ?, ?)",
                    rows,
                )
            else:
                conn.executemany(
                    "INSERT INTO posts (platform, text, timestamp, location) VALUES (?, ?, ?, ?)",
                    rows,
                )
            after = conn.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
            added = after - before
    except Exception as e:
        return 0, str(e)
    return added, None


def load_all_posts() -> pd.DataFrame:
    """Load all posts from SQLite in unified schema."""
    _ensure_db()
    with sqlite3.connect(_DB_PATH) as conn:
        try:
            cols = [r[1] for r in conn.execute("PRAGMA table_info(posts)").fetchall()]
            if "location" in cols:
                q = "SELECT platform, text, timestamp, location FROM posts ORDER BY timestamp DESC"
            else:
                q = "SELECT platform, text, timestamp FROM posts ORDER BY timestamp DESC"
            return pd.read_sql_query(q, conn)
        except Exception:
            return pd.read_sql_query("SELECT platform, text, timestamp FROM posts ORDER BY timestamp DESC", conn)

