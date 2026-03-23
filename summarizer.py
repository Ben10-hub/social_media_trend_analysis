"""
Local extractive summarization utilities for Streamlit dashboard.

No external APIs. Uses Sumy (LSA) when available; falls back to TF-IDF sentence ranking.
"""

from __future__ import annotations

import re
from collections import Counter

import pandas as pd


_WORD_RE = re.compile(r"[A-Za-z]{2,}")


def _normalize_space(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())


def _is_long_enough(text: str, min_words: int = 5) -> bool:
    if not isinstance(text, str):
        return False
    return len(_WORD_RE.findall(text)) >= min_words


def _truncate(text: str, max_chars: int = 220) -> str:
    """
    Soft-limit very long posts so the summary stays compact.
    """
    if not isinstance(text, str):
        text = str(text)
    text = text.strip()
    if len(text) <= max_chars:
        return text
    cut = text[: max_chars - 3].rstrip()
    # avoid cutting in the middle of a word if possible
    last_space = cut.rfind(" ")
    if last_space > max_chars * 0.6:
        cut = cut[:last_space]
    return cut + "..."


def get_top_sentences(df: pd.DataFrame, top_n: int = 10):
    """
    Pick top-N representative posts using TF-IDF scoring.

    - Filters out posts with < 5 words
    - Returns list[str] of top sentences/posts
    """
    if df is None or df.empty or "text" not in df.columns:
        return []
    try:
        texts = [str(t) for t in df["text"].tolist()]
        texts = [_normalize_space(t) for t in texts if _is_long_enough(t, 5)]
        if not texts:
            return []

        from sklearn.feature_extraction.text import TfidfVectorizer

        vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=1, max_features=5000)
        X = vec.fit_transform(texts)
        # Score each sentence by total TF-IDF weight.
        scores = X.sum(axis=1).A.ravel()
        order = scores.argsort()[::-1]
        top = []
        seen = set()
        for idx in order[: max(top_n * 3, top_n)]:
            s = texts[int(idx)]
            key = s.lower()
            if key in seen:
                continue
            seen.add(key)
            top.append(s)
            if len(top) >= top_n:
                break
        return top
    except Exception:
        return []


def extractive_summary(df: pd.DataFrame, num_sentences: int = 20) -> str:
    """
    Extractive summary using Sumy LSA. Returns bullet-style string.

    Fallback: TF-IDF top sentences.
    """
    if df is None or df.empty or "text" not in df.columns:
        return ""
    try:
        texts = [str(t) for t in df["text"].tolist()]
        texts = [_normalize_space(t) for t in texts if _is_long_enough(t, 5)]
        if len(texts) < 1:
            return ""

        doc = "\n".join(texts)

        try:
            from sumy.parsers.plaintext import PlaintextParser
            from sumy.summarizers.lsa import LsaSummarizer
            from sumy.nlp.tokenizers import Tokenizer

            parser = PlaintextParser.from_string(doc, Tokenizer("english"))
            summarizer = LsaSummarizer()
            sents = summarizer(parser.document, max(1, int(num_sentences)))
            bullets = []
            for s in sents:
                line = _normalize_space(str(s))
                if _is_long_enough(line, 5):
                    bullets.append(_truncate(line))
            if bullets:
                return "\n".join([f"- {b}" for b in bullets[:num_sentences]])
        except Exception:
            # Sumy unavailable or failed; fall back below.
            pass

        top = get_top_sentences(df, top_n=max(1, int(num_sentences)))
        return "\n".join([f"- {_truncate(t)}" for t in top[:num_sentences]]) if top else ""
    except Exception:
        top = get_top_sentences(df, top_n=max(1, int(num_sentences)))
        return "\n".join([f"- {_truncate(t)}" for t in top[:num_sentences]]) if top else ""


def get_discussion_themes(df: pd.DataFrame, top_n: int = 5):
    """
    Extract recurring keyword themes using a simple Counter-based approach.
    Returns list[tuple[str,int]].
    """
    if df is None or df.empty or "text" not in df.columns:
        return []
    try:
        # Prefer cleaned tokens if available to avoid noisy words.
        source = df["clean_text"] if "clean_text" in df.columns else df["text"]
        c = Counter()
        for t in source.astype(str).tolist():
            toks = [w.lower() for w in _WORD_RE.findall(t)]
            c.update(toks)
        # Filter extremely common/low-signal tokens (small hardcoded list).
        stop = {
            "the",
            "and",
            "for",
            "with",
            "this",
            "that",
            "have",
            "from",
            "they",
            "you",
            "your",
            "are",
            "was",
            "were",
            "but",
            "not",
            "all",
            "just",
            "about",
            "what",
            "will",
            "can",
            "has",
            "have",
            "people",
            "one",
            "like",
            "time",
            "today",
            "now",
            "new",
            "get",
            "got",
            "make",
            "made",
            "also",
            "really",
        }
        items = [(w, n) for (w, n) in c.most_common(max(50, top_n * 10)) if w not in stop]
        return items[:top_n]
    except Exception:
        return []


def generate_discussion_snapshot(df: pd.DataFrame):
    """
    Master function: creates a snapshot dict that the UI can render.
    """
    if df is None or df.empty:
        return {
            "summary": "",
            "themes": [],
            "total_posts": 0,
            "timeframe": "All time",
            "sentiment_mix": {"positive": 0, "neutral": 0, "negative": 0},
        }

    total_posts = int(len(df))

    # Sentiment mix (percentages) when available.
    mix = {"positive": 0, "neutral": 0, "negative": 0}
    try:
        if "sentiment" in df.columns and total_posts > 0:
            vc = df["sentiment"].astype(str).str.lower().value_counts()
            mix = {
                "positive": int(round(100 * float(vc.get("positive", 0)) / total_posts)),
                "neutral": int(round(100 * float(vc.get("neutral", 0)) / total_posts)),
                "negative": int(round(100 * float(vc.get("negative", 0)) / total_posts)),
            }
    except Exception:
        pass

    themes_pairs = get_discussion_themes(df, top_n=5)
    themes = [w.upper() if len(w) <= 4 else w.title() for (w, _) in themes_pairs]

    # Aim for a compact set of representative bullets.
    bullets = extractive_summary(df, num_sentences=8)
    # Build a short, human-readable snapshot paragraph.
    try:
        lines: list[str] = []
        if themes:
            theme_part = ", ".join(themes[:5])
            lines.append(f"People are mainly talking about {theme_part}.")

        # Add sentiment interpretation if available.
        try:
            pos = mix.get("positive", 0)
            neu = mix.get("neutral", 0)
            neg = mix.get("negative", 0)
            if pos or neu or neg:
                dominant = max(("positive", pos), ("neutral", neu), ("negative", neg), key=lambda x: x[1])[0]
                if dominant == "positive":
                    trend = "overall tone is mostly positive"
                elif dominant == "negative":
                    trend = "overall tone is mostly negative"
                else:
                    trend = "overall tone is fairly mixed and neutral"
                lines.append(f"Out of {total_posts} posts, the {trend} "
                             f"({pos}% positive, {neu}% neutral, {neg}% negative).")
        except Exception:
            pass

        # Optionally append a few short example bullets.
        if bullets:
            lines.append("Some representative opinions:")
            # Keep only first few bullets to avoid overwhelming text.
            for b in bullets.splitlines()[:6]:
                lines.append(b)

        para = "\n".join(lines).strip()
    except Exception:
        para = bullets or ""

    return {
        "summary": para,
        "themes": themes,
        "total_posts": total_posts,
        # UI will override timeframe based on selection
        "timeframe": "All time",
        "sentiment_mix": mix,
    }

