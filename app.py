import io
import os
import re
import string
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


_PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("MPLCONFIGDIR", os.path.join(_PROJECT_DIR, ".mplconfig"))
os.makedirs(os.environ["MPLCONFIGDIR"], exist_ok=True)

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from gensim import corpora
from gensim.models.ldamodel import LdaModel
from sklearn.feature_extraction.text import TfidfVectorizer
from wordcloud import WordCloud


try:
    from adapters.csv_adapter import load_csv_unified
    from adapters.reddit_adapter import fetch_reddit_posts
    from adapters.twitter_adapter import fetch_twitter_posts
    from adapters.youtube_adapter import fetch_youtube_trending, quick_youtube_scrape
    from adapters.instagram_adapter import fetch_instagram_trending, quick_instagram_scrape
    from data_store import append_posts, get_db_path, load_all_posts
    from time_analysis import compute_trends_over_time, trend_growth_rate
    from subquery_search import SubquerySearch
    _HAS_ADAPTERS = True
except ImportError:
    _HAS_ADAPTERS = False

try:
    from summarizer import generate_discussion_snapshot
    _HAS_SUMMARY = True
except Exception:
    _HAS_SUMMARY = False

try:
    import requests
    _HAS_REQUESTS = True
except ImportError:
    _HAS_REQUESTS = False

try:
    import feedparser
    _HAS_FEEDPARSER = True
except ImportError:
    _HAS_FEEDPARSER = False


def quick_reddit_scrape(subreddit: str = "technology", limit: int = 25):
    """
    Scrape Reddit /r/{subreddit}/new via JSON (no API key).
    Returns (DataFrame with platform|text|timestamp, None) on success,
    (None, error_message) on failure.
    """
    if not _HAS_REQUESTS:
        return None, "requests library not installed"
    subreddit = (subreddit or "technology").strip().lower() or "technology"
    try:
        ua = "Mozilla/5.0 (compatible; trend-analysis-app/1.0; +https://streamlit.io)"

        # Prefer RSS (often less restricted than JSON).
        if _HAS_FEEDPARSER:
            try:
                rss_url = f"https://www.reddit.com/r/{subreddit}/new/.rss?limit={limit}&t={int(time.time())}"
                feed = feedparser.parse(rss_url)
                entries = getattr(feed, "entries", None) or []
                rows = []
                for e in entries[:limit]:
                    title = (getattr(e, "title", None) or "").strip()
                    summary = (getattr(e, "summary", None) or "").strip()
                    text = (title + " " + summary).strip() or title
                    published = getattr(e, "published", None) or getattr(e, "updated", None)
                    ts = published.strip() if isinstance(published, str) and published.strip() else datetime.now(timezone.utc).isoformat()
                    if text:
                        rows.append({"platform": "reddit", "text": text, "timestamp": ts})
                if rows:
                    return pd.DataFrame(rows, columns=["platform", "text", "timestamp"]), None
            except Exception:
                pass

        # Fallback to JSON (may 403 depending on Reddit restrictions).
        url = f"https://www.reddit.com/r/{subreddit}/new.json?limit={limit}&t={int(time.time())}"
        resp = requests.get(url, headers={"User-Agent": ua}, timeout=15)
        if resp.status_code == 404:
            return None, f"Subreddit r/{subreddit} not found or not accessible (404). Try another, e.g. technology, Python, programming."
        resp.raise_for_status()
        data = resp.json()
        children = data.get("data", {}).get("children", [])
        rows = []
        for child in children:
            d = child.get("data", {})
            title = (d.get("title") or "")
            selftext = (d.get("selftext") or "")
            text = (title + " " + selftext).strip() or title
            created_utc = d.get("created_utc")
            if created_utc is not None:
                ts = datetime.fromtimestamp(int(created_utc), tz=timezone.utc).isoformat()
            else:
                ts = datetime.now(timezone.utc).isoformat()
            rows.append({"platform": "reddit", "text": text, "timestamp": ts})
        if not rows:
            return None, "No posts returned"
        return pd.DataFrame(rows, columns=["platform", "text", "timestamp"]), None
    except Exception as e:
        return None, str(e)


def quick_x_scrape(query: str = "AI", limit: int = 30, instance_base: str = "https://nitter.net"):
    """
    Scrape X (Twitter) via Nitter RSS (no API key).
    Returns (DataFrame with platform|text|timestamp, None) on success,
    (None, error_message) on failure.
    """
    if not _HAS_FEEDPARSER:
        return None, "feedparser library not installed"
    try:
        import urllib.parse

        # Nitter search RSS — use q=... as recommended. Some instances may still
        # restrict or rate-limit server-side requests, or return empty feeds.
        base = (instance_base or "https://nitter.net").strip().rstrip("/")
        base_url = base + "/search/rss?q=" + urllib.parse.quote(query)

        # First attempt: direct feedparser call.
        feed = feedparser.parse(base_url)

        # If we hit a redirect/SSL/parse problem and requests is available, retry
        # with requests (verify=False) and let feedparser only handle parsing.
        status = getattr(feed, "status", None)
        bozo = getattr(feed, "bozo", 0)
        bozo_exc = getattr(feed, "bozo_exception", None)
        ssl_hint = "CERTIFICATE_VERIFY_FAILED"
        if _HAS_REQUESTS and (
            (status and status in (301, 302, 307, 308))
            or (bozo and bozo_exc and ssl_hint in str(bozo_exc))
        ):
            try:
                resp = requests.get(base_url, headers={"User-Agent": "trend-analysis-app/1.0"}, timeout=15, verify=False)
                resp.raise_for_status()
                feed = feedparser.parse(resp.text)
            except Exception:
                # If the fallback transport also fails, we keep the original feed
                # so that the diagnostic message below still has context.
                pass

        # FeedParserDict usually exposes .entries; fall back to dict-style if needed.
        entries = getattr(feed, "entries", None)
        if entries is None and hasattr(feed, "get"):
            entries = feed.get("entries", [])
        if entries is None:
            entries = []

        rows = []
        for entry in entries[:limit]:
            # entry is a FeedParserDict; attribute and dict access both work.
            title = getattr(entry, "title", None)
            if not title and isinstance(entry, dict):
                title = entry.get("title")
            text = (title or "").strip()

            published = getattr(entry, "published", None)
            if not published and isinstance(entry, dict):
                published = entry.get("published")
            if isinstance(published, str) and published.strip():
                ts = published
            else:
                ts = datetime.now(timezone.utc).isoformat()

            if text:
                rows.append({"platform": "x", "text": text, "timestamp": ts})

        if not rows:
            # Surface more helpful diagnostics if available.
            status = getattr(feed, "status", None)
            if status and status != 200:
                return None, f"Nitter RSS HTTP status {status}; search may be blocked, redirected, or rate-limited."
            if getattr(feed, "bozo", 0):
                bex = getattr(feed, "bozo_exception", None)
                if bex:
                    return None, f"Nitter RSS parse error: {bex}"
            return None, (
                "No entries in feed (query may be too restrictive or the Nitter instance returned an empty feed). "
                f"Try a different instance URL (current: {base})."
            )

        return pd.DataFrame(rows, columns=["platform", "text", "timestamp"]), None
    except Exception as e:
        return None, str(e)


def safe_word_tokenize(text: str) -> list[str]:
    """
    Tokenize text with NLTK when available; fall back to a simple regex tokenizer.
    Defined at module level so Streamlit can cache it safely.
    """
    try:
        from nltk.tokenize import word_tokenize

        return word_tokenize(text)
    except Exception:
        return re.findall(r"[a-zA-Z]+", text)


def _lazy_nltk_setup() -> None:
    import nltk
    import ssl

    # Make NLTK data downloads deterministic and writable for local runs.
    # This avoids LookupError in environments where the default NLTK_DATA paths
    # are not present or not writable.
    download_dir = os.path.join(_PROJECT_DIR, ".nltk_data")
    os.makedirs(download_dir, exist_ok=True)
    os.environ.setdefault("NLTK_DATA", download_dir)
    if download_dir not in nltk.data.path:
        nltk.data.path.insert(0, download_dir)

    needed = [
        ("punkt", "tokenizers/punkt"),
        ("punkt_tab", "tokenizers/punkt_tab"),
        ("stopwords", "corpora/stopwords"),
        ("wordnet", "corpora/wordnet"),
        ("omw-1.4", "corpora/omw-1.4"),
        ("vader_lexicon", "sentiment/vader_lexicon"),
    ]

    def _download(pkg: str) -> None:
        # First try normal SSL verification; if the user's Python install is missing
        # certs (common on macOS), fall back to an unverified context.
        ok = False
        try:
            ok = bool(nltk.download(pkg, download_dir=download_dir, quiet=True))
        except Exception:
            ok = False
        if ok:
            return
        old_ctx = ssl._create_default_https_context
        try:
            ssl._create_default_https_context = ssl._create_unverified_context
            nltk.download(pkg, download_dir=download_dir, quiet=True)
        finally:
            ssl._create_default_https_context = old_ctx

    for pkg, path in needed:
        try:
            nltk.data.find(path)
        except LookupError:
            _download(pkg)


URL_RE = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
MENTION_RE = re.compile(r"@\w+")
HASHTAG_RE = re.compile(r"#\w+")
NON_ALPHA_RE = re.compile(r"[^a-zA-Z\s]")
MULTISPACE_RE = re.compile(r"\s+")


@st.cache_data(show_spinner=False)
def load_csv(file_bytes: bytes) -> pd.DataFrame:
    return pd.read_csv(io.BytesIO(file_bytes))


@st.cache_resource(show_spinner=False)
def get_nlp_tools():
    _lazy_nltk_setup()
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
    from nltk.sentiment import SentimentIntensityAnalyzer

    stop = set(stopwords.words("english"))
    lemmatizer = WordNetLemmatizer()
    sia = SentimentIntensityAnalyzer()
    return stop, lemmatizer, safe_word_tokenize, sia


def extract_hashtags(text: str) -> list[str]:
    if not isinstance(text, str):
        return []
    return [h.lower() for h in HASHTAG_RE.findall(text)]


def basic_clean(text: str) -> str:
    if not isinstance(text, str):
        return ""
    t = text
    t = URL_RE.sub(" ", t)
    t = MENTION_RE.sub(" ", t)
    t = t.replace("\n", " ").replace("\r", " ")
    t = t.lower()
    t = t.translate(str.maketrans({c: " " for c in string.punctuation}))
    t = NON_ALPHA_RE.sub(" ", t)
    t = MULTISPACE_RE.sub(" ", t).strip()
    return t


def tokenize_lemmatize(text: str, stopwords_set, lemmatizer, word_tokenize_fn) -> list[str]:
    cleaned = basic_clean(text)
    if not cleaned:
        return []
    tokens = word_tokenize_fn(cleaned)
    out: list[str] = []
    for tok in tokens:
        if len(tok) < 2:
            continue
        if tok in stopwords_set:
            continue
        out.append(lemmatizer.lemmatize(tok))
    return out


@st.cache_data(show_spinner=False)
def preprocess_texts(texts: list[str]):
    stop, lemmatizer, word_tokenize_fn, _ = get_nlp_tools()
    tokens_list = [tokenize_lemmatize(t, stop, lemmatizer, word_tokenize_fn) for t in texts]
    cleaned_texts = [" ".join(toks) for toks in tokens_list]
    return cleaned_texts, tokens_list


@st.cache_data(show_spinner=False)
def compute_keyword_frequency(tokens_list: list[list[str]], top_k: int) -> pd.DataFrame:
    c = Counter()
    for toks in tokens_list:
        c.update(toks)
    rows = c.most_common(top_k)
    return pd.DataFrame(rows, columns=["keyword", "count"])


@st.cache_data(show_spinner=False)
def compute_hashtag_frequency(raw_texts: list[str], top_k: int) -> pd.DataFrame:
    c = Counter()
    for t in raw_texts:
        c.update(extract_hashtags(t))
    rows = c.most_common(top_k)
    return pd.DataFrame(rows, columns=["hashtag", "count"])


@st.cache_data(show_spinner=False)
def compute_tfidf_top_terms(cleaned_texts: list[str], top_k: int) -> pd.DataFrame:
    vec = TfidfVectorizer(
        max_features=max(2000, top_k * 10),
        ngram_range=(1, 2),
        min_df=2,
    )
    X = vec.fit_transform(cleaned_texts)
    scores = np.asarray(X.mean(axis=0)).ravel()
    terms = np.array(vec.get_feature_names_out())
    if scores.size == 0:
        return pd.DataFrame(columns=["term", "score"])
    idx = np.argsort(scores)[::-1][:top_k]
    return pd.DataFrame({"term": terms[idx], "score": scores[idx]})


@st.cache_data(show_spinner=False)
def compute_lda_topics(tokens_list: list[list[str]], num_topics: int, passes: int = 10, random_state: int = 42):
    filtered_pairs = [(i, toks) for i, toks in enumerate(tokens_list) if len(toks) >= 3]
    filtered_indices = [i for i, _ in filtered_pairs]
    filtered = [toks for _, toks in filtered_pairs]
    if len(filtered) < max(10, num_topics * 2):
        return None

    dictionary = corpora.Dictionary(filtered)
    dictionary.filter_extremes(no_below=2, no_above=0.6, keep_n=5000)
    corpus = [dictionary.doc2bow(toks) for toks in filtered]
    if not corpus or len(dictionary) == 0:
        return None

    lda = LdaModel(
        corpus=corpus,
        id2word=dictionary,
        num_topics=num_topics,
        passes=passes,
        random_state=random_state,
        alpha="auto",
        per_word_topics=False,
    )
    return {
        "lda": lda,
        "dictionary": dictionary,
        "corpus": corpus,
        "filtered_tokens": filtered,
        "filtered_indices": filtered_indices,
    }


def lda_topics_table(lda: LdaModel, num_words: int = 8) -> pd.DataFrame:
    rows = []
    for topic_id in range(lda.num_topics):
        terms = lda.show_topic(topic_id, topn=num_words)
        rows.append(
            {
                "topic": f"Topic {topic_id}",
                "top_words": ", ".join([w for w, _ in terms]),
            }
        )
    return pd.DataFrame(rows)


@st.cache_data(show_spinner=False)
def vader_sentiment(texts: list[str]) -> pd.DataFrame:
    _, _, _, sia = get_nlp_tools()
    comp = []
    label = []
    for t in texts:
        s = sia.polarity_scores(t if isinstance(t, str) else "")
        c = float(s.get("compound", 0.0))
        comp.append(c)
        if c >= 0.05:
            label.append("Positive")
        elif c <= -0.05:
            label.append("Negative")
        else:
            label.append("Neutral")
    return pd.DataFrame({"compound": comp, "sentiment": label})


def plot_bar(df: pd.DataFrame, x: str, y: str, title: str):
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.barh(df[x][::-1], df[y][::-1], color="#4e79a7")
    ax.set_title(title)
    ax.set_xlabel(y)
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    return fig


def plot_pie_sentiment(counts: pd.Series, title: str):
    fig, ax = plt.subplots(figsize=(5.8, 4.2))
    order = ["Positive", "Neutral", "Negative"]
    labels = [k for k in order if k in counts.index]
    sizes = [int(counts[k]) for k in labels]
    colors = {"Positive": "#59a14f", "Neutral": "#bab0ac", "Negative": "#e15759"}
    ax.pie(
        sizes,
        labels=labels,
        autopct=lambda p: f"{p:.0f}%",
        colors=[colors[l] for l in labels],
        startangle=90,
        textprops={"fontsize": 10},
    )
    ax.set_title(title)
    fig.tight_layout()
    return fig


def make_wordcloud(tokens_list: list[list[str]]):
    all_words = " ".join([" ".join(toks) for toks in tokens_list if toks])
    if not all_words.strip():
        return None
    wc = WordCloud(width=900, height=450, background_color="white", collocations=False).generate(all_words)
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    fig.tight_layout()
    return fig


def infer_text_column(columns: list[str]) -> str | None:
    if not columns:
        return None
    preferred = [
        "text",
        "clean_text",
        "clean_comment",
        "comment",
        "content",
        "body",
        "post",
        "tweet",
        "message",
    ]
    cols_lower = {c.lower(): c for c in columns}
    for p in preferred:
        if p in cols_lower:
            return cols_lower[p]
    for c in columns:
        cl = c.lower()
        if "text" in cl or "comment" in cl or "tweet" in cl or "post" in cl:
            return c
    return None


def main():
    st.set_page_config(page_title="Trend & Sentiment Analyzer", layout="wide")

    if "live_mode" not in st.session_state:
        st.session_state["live_mode"] = False
    if "refresh_interval" not in st.session_state:
        st.session_state["refresh_interval"] = 30
    if "last_live_refresh" not in st.session_state:
        st.session_state["last_live_refresh"] = 0.0

    with st.sidebar:
        st.title("Controls")
        st.caption("Choose data source or upload a CSV with a text column.")

        top_n = st.slider("Number of trends", min_value=5, max_value=50, value=15, step=1)
        lda_topics_n = st.slider("LDA topics", min_value=2, max_value=12, value=5, step=1)
        lda_passes = st.slider("LDA passes", min_value=5, max_value=30, value=10, step=1)
        time_interval = st.selectbox("Time grouping", options=["hour", "minute"], index=0)

        st.divider()

        data_source = st.radio(
            "Data source",
            [
                "Sample",
                "Upload CSV",
                "Quick Reddit",
                "Quick X",
                "Quick YouTube",
                "Quick Instagram",
                "Hacker News",
                "News RSS",
                "Load from collected",
            ],
            index=0,
        )
        uploaded_files = (
            st.file_uploader("Upload CSV(s)", type=["csv"], accept_multiple_files=True)
            if data_source == "Upload CSV"
            else None
        )
        quick_reddit_sub = "technology"
        quick_reddit_limit = 25
        quick_x_query = "AI"
        quick_x_limit = 30
        quick_youtube_query = "trending"
        quick_youtube_limit = 30
        quick_instagram_hashtag = "trending"
        quick_instagram_limit = 30
        
        if data_source == "Quick Reddit":
            quick_reddit_sub = st.text_input(
                "Subreddit",
                value="technology",
                key="quick_reddit_sub",
                help="e.g. technology, Python, programming. Some subreddits (e.g. r/ai) may return 404.",
            )
            quick_reddit_limit = int(st.number_input("Posts to fetch", min_value=5, max_value=100, value=25, key="quick_reddit_lim"))
        if data_source == "Quick X":
            quick_x_query = st.text_input("Search query", value="AI", key="quick_x_query")
            quick_x_limit = int(st.number_input("Posts to fetch", min_value=5, max_value=100, value=30, key="quick_x_lim"))
            quick_x_instance = st.text_input(
                "Nitter instance URL",
                value="https://nitter.net",
                key="quick_x_instance",
                help="If this instance returns empty/blocked feeds, try another public Nitter instance URL.",
            )
        if data_source == "Quick YouTube":
            quick_youtube_query = st.text_input("Search query", value="trending", key="quick_youtube_query")
            quick_youtube_limit = int(st.number_input("Videos to fetch", min_value=5, max_value=100, value=30, key="quick_youtube_lim"))
        if data_source == "Quick Instagram":
            quick_instagram_hashtag = st.text_input("Hashtag (without #)", value="trending", key="quick_instagram_hashtag")
            quick_instagram_limit = int(st.number_input("Posts to fetch", min_value=5, max_value=100, value=30, key="quick_instagram_lim"))

    st.title("Hybrid Social Media Trend & Sentiment Analysis")
    st.caption("Trends (hashtags/keywords/TF‑IDF/LDA) + Sentiment (VADER) + Real-time & time-based analytics.")

    # ── Live Mode Status Indicator ──────────────────────────────────────────
    if st.session_state.get("live_mode", False):
        st.success(f"""
        🟢 **Live Mode Active**
        - Refresh interval: {st.session_state.get("refresh_interval", 30)}s
        - Last updated: {datetime.now().strftime("%H:%M:%S")}
        """, icon="✅")
    else:
        st.info("⚪ **Manual Mode** — Select data source and click Collect buttons manually.", icon="ℹ️")

    # ── Live Rerun Logic ───────────────────────────────────────────────────
    if st.session_state.get("live_mode", False):
        now = time.time()
        last_refresh = st.session_state.get("last_live_refresh", 0.0)
        refresh_interval = st.session_state.get("refresh_interval", 30)
        if now - last_refresh >= refresh_interval:
            st.session_state["last_live_refresh"] = now
            time.sleep(0.1)
            st.rerun()

    df = None
    err_msg = None

    if data_source == "Sample":
        try:
            sample_path = Path(__file__).resolve().parent / "data" / "sample_social_posts.csv"
            if _HAS_ADAPTERS:
                df = load_csv_unified(file_path=str(sample_path), platform_default="sample")
            else:
                df = pd.read_csv(sample_path)
                df["platform"] = "sample"
                df["timestamp"] = df["created_at"].astype(str) if "created_at" in df.columns else pd.Timestamp.utcnow().isoformat()
                df["text"] = df["text"].astype(str)
        except Exception as e:
            err_msg = str(e)
    elif data_source == "Upload CSV":
        if uploaded_files is not None and len(uploaded_files) > 0:
            try:
                list_of_dfs = []
                single_file = len(uploaded_files) == 1
                for f in uploaded_files:
                    fname = (getattr(f, "name", None) or "csv").replace(".csv", "").strip() or "csv"
                    platform_default = "csv" if single_file else fname
                    if _HAS_ADAPTERS:
                        one_df = load_csv_unified(file_bytes=f.getvalue(), platform_default=platform_default)
                    else:
                        one_df = load_csv(f.getvalue())
                        one_df["platform"] = platform_default
                        if "timestamp" not in one_df.columns:
                            one_df["timestamp"] = pd.Timestamp.utcnow().isoformat()
                        else:
                            one_df["timestamp"] = one_df["timestamp"].astype(str)
                        text_col = infer_text_column([c for c in one_df.columns if one_df[c].dtype == "object"] or list(one_df.columns))
                        if text_col:
                            one_df["text"] = one_df[text_col].astype(str)
                        else:
                            one_df["text"] = one_df.iloc[:, 0].astype(str) if len(one_df.columns) > 0 else ""
                        one_df = one_df[["platform", "text", "timestamp"]].copy()
                    list_of_dfs.append(one_df)
                df = pd.concat(list_of_dfs, ignore_index=True)
            except Exception as e:
                err_msg = str(e)
        else:
            st.info("Upload at least one CSV file.")
            st.stop()
    elif data_source == "Quick Reddit":
        with st.spinner("Quick scraping Reddit..."):
            df, err = quick_reddit_scrape(subreddit=quick_reddit_sub, limit=quick_reddit_limit)
        if err or df is None or df.empty:
            st.warning(f"Quick Reddit scrape failed: {err or 'No data'}. Using sample dataset.")
            try:
                sample_path = Path(__file__).resolve().parent / "data" / "sample_social_posts.csv"
                if _HAS_ADAPTERS:
                    df = load_csv_unified(file_path=str(sample_path), platform_default="sample")
                else:
                    df = pd.read_csv(sample_path)
                    df["platform"] = "sample"
                    df["timestamp"] = df["created_at"].astype(str) if "created_at" in df.columns else pd.Timestamp.utcnow().isoformat()
                    df["text"] = df["text"].astype(str)
            except Exception as e:
                err_msg = str(e)
    elif data_source == "Quick X":
        if not _HAS_FEEDPARSER:
            st.warning("feedparser not installed. Using sample dataset.")
            try:
                sample_path = Path(__file__).resolve().parent / "data" / "sample_social_posts.csv"
                if _HAS_ADAPTERS:
                    df = load_csv_unified(file_path=str(sample_path), platform_default="sample")
                else:
                    df = pd.read_csv(sample_path)
                    df["platform"] = "sample"
                    df["timestamp"] = df["created_at"].astype(str) if "created_at" in df.columns else pd.Timestamp.utcnow().isoformat()
                    df["text"] = df["text"].astype(str)
            except Exception as e:
                err_msg = str(e)
        else:
            with st.spinner("Quick scraping X (Nitter RSS)..."):
                df, err = quick_x_scrape(query=quick_x_query, limit=quick_x_limit, instance_base=quick_x_instance)
            if err or df is None or df.empty:
                st.warning(f"Quick X scrape failed: {err or 'No data'}. Using sample dataset.")
                try:
                    sample_path = Path(__file__).resolve().parent / "data" / "sample_social_posts.csv"
                    if _HAS_ADAPTERS:
                        df = load_csv_unified(file_path=str(sample_path), platform_default="sample")
                    else:
                        df = pd.read_csv(sample_path)
                        df["platform"] = "sample"
                        df["timestamp"] = df["created_at"].astype(str) if "created_at" in df.columns else pd.Timestamp.utcnow().isoformat()
                        df["text"] = df["text"].astype(str)
                except Exception as e:
                    err_msg = str(e)
    elif data_source == "Quick YouTube":
        with st.spinner("Quick scraping YouTube..."):
            df, err = quick_youtube_scrape(query=quick_youtube_query, limit=quick_youtube_limit)
        if err or df is None or df.empty:
            st.warning(f"Quick YouTube scrape failed: {err or 'No data'}. Using sample dataset.")
            try:
                sample_path = Path(__file__).resolve().parent / "data" / "sample_social_posts.csv"
                if _HAS_ADAPTERS:
                    df = load_csv_unified(file_path=str(sample_path), platform_default="sample")
                else:
                    df = pd.read_csv(sample_path)
                    df["platform"] = "sample"
                    df["timestamp"] = df["created_at"].astype(str) if "created_at" in df.columns else pd.Timestamp.utcnow().isoformat()
                    df["text"] = df["text"].astype(str)
            except Exception as e:
                err_msg = str(e)
    elif data_source == "Quick Instagram":
        with st.spinner("Quick scraping Instagram..."):
            df, err = quick_instagram_scrape(hashtag=quick_instagram_hashtag, limit=quick_instagram_limit)
        if err or df is None or df.empty:
            st.warning(f"Quick Instagram scrape failed: {err or 'No data'}. Using sample dataset.")
            try:
                sample_path = Path(__file__).resolve().parent / "data" / "sample_social_posts.csv"
                if _HAS_ADAPTERS:
                    df = load_csv_unified(file_path=str(sample_path), platform_default="sample")
                else:
                    df = pd.read_csv(sample_path)
                    df["platform"] = "sample"
                    df["timestamp"] = df["created_at"].astype(str) if "created_at" in df.columns else pd.Timestamp.utcnow().isoformat()
                    df["text"] = df["text"].astype(str)
            except Exception as e:
                err_msg = str(e)
    elif data_source == "Load from collected":
        if _HAS_ADAPTERS:
            try:
                df = load_all_posts()
                if df is None or df.empty:
                    st.warning("No collected data yet. Use Collect Now or run collect_real_time.py.")
                    st.info("Falling back to sample dataset.")
                    sample_path = Path(__file__).resolve().parent / "data" / "sample_social_posts.csv"
                    df = load_csv_unified(file_path=str(sample_path), platform_default="sample")
                else:
                    pass
            except Exception as e:
                err_msg = str(e)
                st.warning(f"Error loading collected data: {e}. Using sample dataset.")
                sample_path = Path(__file__).resolve().parent / "data" / "sample_social_posts.csv"
                df = load_csv_unified(file_path=str(sample_path), platform_default="sample")
        else:
            st.warning("Collectors not available. Use sample or upload.")
            st.stop()
    elif data_source == "Hacker News":
        with st.spinner("Fetching Hacker News top stories..."):
            try:
                import requests
                top_ids_resp = requests.get(
                    "https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10
                )
                top_ids = top_ids_resp.json()[:40]
                rows = []
                for item_id in top_ids:
                    try:
                        item = requests.get(
                            f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json",
                            timeout=5,
                        ).json()
                        title = item.get("title", "")
                        url = item.get("url", "")
                        text = (title + " " + url).strip()
                        ts = datetime.fromtimestamp(
                            item.get("time", 0), tz=timezone.utc
                        ).isoformat()
                        if text:
                            rows.append({"platform": "hackernews", "text": text, "timestamp": ts})
                    except Exception:
                        continue
                if rows:
                    df = pd.DataFrame(rows, columns=["platform", "text", "timestamp"])
                else:
                    raise ValueError("No stories returned")
            except Exception as e:
                st.warning(f"Hacker News fetch failed: {e}. Using sample dataset.")
                sample_path = Path(__file__).resolve().parent / "data" / "sample_social_posts.csv"
                df = load_csv_unified(file_path=str(sample_path), platform_default="sample") if _HAS_ADAPTERS else pd.read_csv(sample_path)
    elif data_source == "News RSS":
        with st.sidebar:
            rss_options = {
                "TechCrunch": "https://techcrunch.com/feed/",
                "BBC Technology": "http://feeds.bbci.co.uk/news/technology/rss.xml",
                "The Verge": "https://www.theverge.com/rss/index.xml",
                "Wired": "https://www.wired.com/feed/rss",
            }
            rss_choice = st.selectbox("RSS Feed", list(rss_options.keys()))
        with st.spinner(f"Fetching {rss_choice} RSS..."):
            try:
                if not _HAS_FEEDPARSER:
                    raise ImportError("feedparser not installed")
                feed = feedparser.parse(rss_options[rss_choice])
                rows = []
                for entry in feed.entries[:50]:
                    title = getattr(entry, "title", "") or ""
                    summary = getattr(entry, "summary", "") or ""
                    text = (title + " " + summary).strip()
                    published = getattr(entry, "published", None)
                    ts = published if isinstance(published, str) and published else datetime.now(timezone.utc).isoformat()
                    if text:
                        rows.append({"platform": "news_rss", "text": text, "timestamp": ts})
                if rows:
                    df = pd.DataFrame(rows, columns=["platform", "text", "timestamp"])
                else:
                    raise ValueError("No RSS entries found")
            except Exception as e:
                st.warning(f"RSS fetch failed: {e}. Using sample dataset.")
                sample_path = Path(__file__).resolve().parent / "data" / "sample_social_posts.csv"
                df = load_csv_unified(file_path=str(sample_path), platform_default="sample") if _HAS_ADAPTERS else pd.read_csv(sample_path)

    # ── Live Mode Data Reload (auto-refresh from selected source) ─────────
    if st.session_state.get("live_mode", False) and df is not None:
        try:
            if data_source == "Load from collected" and _HAS_ADAPTERS:
                fresh_df = load_all_posts()
                if fresh_df is not None and not fresh_df.empty and len(fresh_df) > len(df):
                    df = fresh_df
            elif data_source == "Quick Reddit":
                fresh, err = quick_reddit_scrape(subreddit=quick_reddit_sub, limit=quick_reddit_limit)
                if not err and fresh is not None and not fresh.empty and len(fresh) > len(df):
                    df = fresh
            elif data_source == "Quick X":
                fresh, err = quick_x_scrape(query=quick_x_query, limit=quick_x_limit, instance_base=quick_x_instance)
                if not err and fresh is not None and not fresh.empty and len(fresh) > len(df):
                    df = fresh
            elif data_source == "Quick YouTube":
                fresh, err = quick_youtube_scrape(query=quick_youtube_query, limit=quick_youtube_limit)
                if not err and fresh is not None and not fresh.empty and len(fresh) > len(df):
                    df = fresh
            elif data_source == "Quick Instagram":
                fresh, err = quick_instagram_scrape(hashtag=quick_instagram_hashtag, limit=quick_instagram_limit)
                if not err and fresh is not None and not fresh.empty and len(fresh) > len(df):
                    df = fresh
        except Exception:
            pass

    if df is None:
        st.error(err_msg or "No data loaded.")
        st.info("Upload a CSV or enable the sample dataset.")
        st.stop()

    if "text" not in df.columns:
        candidate_cols = [c for c in df.columns if df[c].dtype == "object"] or list(df.columns)
        inferred = infer_text_column(candidate_cols)
        if inferred is None:
            st.error("Could not find a text column.")
            st.stop()
        df = df.copy()
        df["text"] = df[inferred].astype(str)
    else:
        df = df.copy()
        df["text"] = df["text"].astype(str)

    if "platform" not in df.columns:
        df["platform"] = data_source.lower().replace(" ", "_")
    if "timestamp" not in df.columns:
        df["timestamp"] = pd.Timestamp.utcnow().isoformat()

    # Real-time collection controls (sidebar)
    if _HAS_ADAPTERS:
        with st.sidebar:
            st.divider()
            st.subheader("Real-time collection")
            if st.button("Collect Reddit (now)", help="Fetch Reddit posts and append to SQLite"):
                with st.spinner("Fetching Reddit..."):
                    rdf, err = fetch_reddit_posts(subreddits=["python", "technology"], limit_per_sub=50)
                if err:
                    st.error(err)
                elif rdf is not None and not rdf.empty:
                    added, aerr = append_posts(rdf, dedup=True)
                    if aerr:
                        st.error(aerr)
                    else:
                        st.success(f"Added {added} new posts. Stored at: {get_db_path()}")
                else:
                    st.warning("No new posts fetched.")

            if st.button("Collect YouTube (now)", help="Fetch YouTube trending via adapter and append to SQLite"):
                with st.spinner("Fetching YouTube..."):
                    ydf, err = fetch_youtube_trending(max_results=50, region_code="US")
                if err:
                    st.error(err)
                elif ydf is not None and not ydf.empty:
                    added, aerr = append_posts(ydf, dedup=True)
                    if aerr:
                        st.error(aerr)
                    else:
                        st.success(f"Added {added} new posts. Stored at: {get_db_path()}")
                else:
                    st.warning("No new posts fetched.")

            if st.button("Collect Instagram (now)", help="Fetch Instagram trending via adapter and append to SQLite"):
                with st.spinner("Fetching Instagram..."):
                    idf, err = fetch_instagram_trending(max_results=50)
                if err:
                    st.error(err)
                elif idf is not None and not idf.empty:
                    added, aerr = append_posts(idf, dedup=True)
                    if aerr:
                        st.error(aerr)
                    else:
                        st.success(f"Added {added} new posts. Stored at: {get_db_path()}")
                else:
                    st.warning("No new posts fetched.")

            st.divider()
            st.subheader("🔴 Live Mode")
            st.session_state["live_mode"] = st.checkbox(
                "Enable Live Mode", value=st.session_state.get("live_mode", False),
                help="Auto-refresh and reload data from selected source every N seconds."
            )
            st.session_state["refresh_interval"] = st.slider(
                "Refresh interval (seconds)",
                min_value=10, max_value=120, value=st.session_state.get("refresh_interval", 30),
                step=5, key="live_refresh_slider"
            )
            if st.session_state.get("live_mode"):
                st.info("💡 Tip: Run `collect_real_time.py` for continuous data ingestion to SQLite.")

    with st.expander("Dataset preview", expanded=True):
        st.dataframe(df.head(30), use_container_width=True)
        st.caption(f"Rows: {len(df):,} | Columns: {len(df.columns)}")
        if data_source == "Quick Reddit":
            st.caption("Reddit ‘new’ feed shows the latest posts; list changes only when new posts are added. Change **Subreddit** in the sidebar for different content.")
        elif data_source == "Quick X":
            st.caption("X results depend on the search query. Change **Search query** in the sidebar for different content.")
        elif data_source == "Quick YouTube":
            st.caption("YouTube no-API scrape via RSS proxy. If results are slow, try a different query.")
        elif data_source == "Quick Instagram":
            st.caption("Instagram no-API scrape via RSS proxy. If results are slow, try a different hashtag.")

    raw_texts = df["text"].tolist()
    cleaned_texts, tokens_list = preprocess_texts(raw_texts)
    df["clean_text"] = cleaned_texts
    df["hashtags"] = [extract_hashtags(t) for t in raw_texts]

    sent_df = vader_sentiment(raw_texts)
    df = pd.concat([df, sent_df], axis=1)

    kw_df = compute_keyword_frequency(tokens_list, top_n)
    ht_df = compute_hashtag_frequency(raw_texts, top_n)
    tfidf_df = compute_tfidf_top_terms(cleaned_texts, top_n)

    lda_pack = compute_lda_topics(tokens_list, num_topics=lda_topics_n, passes=lda_passes)

    tab_overview, tab_trends, tab_topics, tab_timebased, tab_geo, tab_subquery = st.tabs([
        "📊 Overview",
        "📈 Trends",
        "🧠 Topics (LDA)",
        "⏱ Time Trends",
        "🌍 Geographic",
        "🔍 Search",
    ])

    with tab_overview:
        # ── Dataset statistics ──────────────────────────────────────────────
        st.subheader("Dataset Overview")
        vocab_size = len(set(w for toks in tokens_list for w in toks))
        avg_len = df["text"].str.split().str.len().mean()
        o1, o2, o3, o4 = st.columns(4)
        o1.metric("Total Posts", f"{len(df):,}")
        o2.metric("Vocabulary Size", f"{vocab_size:,}")
        o3.metric("Unique Hashtags", f"{len(set(h for hs in df['hashtags'] for h in hs)):,}")
        o4.metric("Avg Post Length", f"{avg_len:.1f} words")

        # ── Sentiment distribution ───────────────────────────────────────────
        st.subheader("Overall Sentiment (VADER)")
        col_pie, col_table = st.columns([1, 1])
        with col_pie:
            counts = df["sentiment"].value_counts()
            fig = plot_pie_sentiment(counts, "Sentiment distribution")
            st.pyplot(fig, clear_figure=True)
        with col_table:
            st.caption("Breakdown by platform")
            if "platform" in df.columns and df["platform"].nunique() > 1:
                pivot = df.groupby("platform")["sentiment"].value_counts(normalize=True).unstack(fill_value=0)
                pivot = pivot.reindex(columns=["Positive", "Neutral", "Negative"], fill_value=0)
                pivot = pivot.applymap(lambda x: f"{x:.1%}")
                st.dataframe(pivot, use_container_width=True)
            else:
                st.caption(f"Avg compound score: **{df['compound'].mean():.3f}**")
                dist = df["sentiment"].value_counts().reset_index()
                dist.columns = ["Sentiment", "Count"]
                st.dataframe(dist, use_container_width=True)

        # ── Model Comparison: VADER vs TextBlob ──────────────────────────────
        with st.expander("🔬 Model Comparison: VADER vs TextBlob (Academic)"):
            st.caption(
                "This section justifies the choice of VADER as the primary sentiment model. "
                "VADER is rule-based and optimised for short, informal social media text. "
                "TextBlob is a general-purpose model that often underperforms on social media."
            )
            try:
                from textblob import TextBlob
                sample_texts = df["text"].dropna().head(200).tolist()
                tb_labels = []
                for t in sample_texts:
                    pol = TextBlob(str(t)).sentiment.polarity
                    if pol > 0.05:
                        tb_labels.append("Positive")
                    elif pol < -0.05:
                        tb_labels.append("Negative")
                    else:
                        tb_labels.append("Neutral")
                vader_labels = df["sentiment"].head(200).tolist()
                agree = sum(v == t for v, t in zip(vader_labels, tb_labels))
                agreement_pct = agree / len(sample_texts) * 100 if sample_texts else 0
                m1, m2, m3 = st.columns(3)
                m1.metric("VADER Positive %", f"{vader_labels.count('Positive') / len(vader_labels):.1%}")
                m2.metric("TextBlob Positive %", f"{tb_labels.count('Positive') / len(tb_labels):.1%}")
                m3.metric("Model Agreement", f"{agreement_pct:.1f}%")
                comp_df = pd.DataFrame({
                    "Model": ["VADER", "TextBlob"],
                    "Positive": [
                        vader_labels.count("Positive") / len(vader_labels),
                        tb_labels.count("Positive") / len(tb_labels),
                    ],
                    "Neutral": [
                        vader_labels.count("Neutral") / len(vader_labels),
                        tb_labels.count("Neutral") / len(tb_labels),
                    ],
                    "Negative": [
                        vader_labels.count("Negative") / len(vader_labels),
                        tb_labels.count("Negative") / len(tb_labels),
                    ],
                })
                fig, ax = plt.subplots(figsize=(7, 3))
                x = np.arange(2)
                width = 0.25
                ax.bar(x - width, comp_df["Positive"], width, label="Positive", color="#59a14f")
                ax.bar(x, comp_df["Neutral"], width, label="Neutral", color="#bab0ac")
                ax.bar(x + width, comp_df["Negative"], width, label="Negative", color="#e15759")
                ax.set_xticks(x)
                ax.set_xticklabels(["VADER", "TextBlob"])
                ax.set_ylabel("Share of posts")
                ax.set_title("VADER vs TextBlob Sentiment Distribution")
                ax.legend()
                fig.tight_layout()
                st.pyplot(fig, clear_figure=True)
                st.caption("VADER is preferred for social media because it handles slang, emojis, and punctuation emphasis (e.g. 'GREAT!!!') — factors TextBlob ignores.")
            except ImportError:
                st.info("Install textblob (`pip install textblob`) to enable this comparison.")
            except Exception as e:
                st.warning(f"Comparison error: {e}")

        # ── Word cloud ───────────────────────────────────────────────────────
        st.subheader("Word Cloud (Frequent Terms)")
        wc_fig = make_wordcloud(tokens_list)
        if wc_fig is None:
            st.warning("Not enough processed text to build a word cloud.")
        else:
            st.pyplot(wc_fig, clear_figure=True, use_container_width=True)

        # ── Sentiment per trend (moved from old Sentiment tab) ───────────────
        st.subheader("Sentiment per Trend (VADER)")
        st.caption("Select a keyword or hashtag to see how people feel about it.")
        trend_mode = st.radio("Trend type", ["Keyword", "Hashtag", "TF‑IDF term"], horizontal=True, key="ov_trend_mode")
        if trend_mode == "Keyword":
            options = kw_df["keyword"].tolist() if not kw_df.empty else []
        elif trend_mode == "Hashtag":
            options = ht_df["hashtag"].tolist() if not ht_df.empty else []
        else:
            options = tfidf_df["term"].tolist() if not tfidf_df.empty else []
        if not options:
            st.info("No trends available to analyze.")
        else:
            selected = st.selectbox("Select a trend", options=options, index=0, key="ov_trend_select")
            if trend_mode == "Hashtag":
                mask = df["text"].str.lower().str.contains(re.escape(selected), na=False)
            else:
                pattern = r"\b" + re.escape(selected.lower()) + r"\b"
                mask = df["clean_text"].str.contains(pattern, regex=True, na=False)
            subset = df.loc[mask].copy()
            st.caption(f"Matching posts: {len(subset):,}")
            if subset.empty:
                st.warning("No matching posts for this trend.")
            else:
                scounts = subset["sentiment"].value_counts()
                st.pyplot(plot_pie_sentiment(scounts, f"Sentiment for: {selected}"), clear_figure=True)
                with st.expander("View matching posts"):
                    st.dataframe(subset[["text", "sentiment", "compound"]].head(100), use_container_width=True)

        # ── Download ─────────────────────────────────────────────────────────
        out = df[["text", "sentiment", "compound", "clean_text"]].copy()
        st.download_button(
            "📥 Download Sentiment Results CSV",
            data=out.to_csv(index=False).encode("utf-8"),
            file_name="sentiment_results.csv",
            mime="text/csv",
        )

    with tab_trends:
        # ── Trend Velocity (growth rate of top keywords over time) ──────────
        if "timestamp" in df.columns and _HAS_ADAPTERS:
            with st.expander("📉 Trend Velocity — Keyword Growth Over Time"):
                st.caption("Shows how fast each keyword is rising or falling. Useful for spotting emerging trends.")
                try:
                    from time_analysis import compute_trends_over_time
                    _, kw_per, _ = compute_trends_over_time(
                        df, text_col="text", ts_col="timestamp", interval="hour", top_k=10
                    )
                    if kw_per is not None and not kw_per.empty and "keyword" in kw_per.columns:
                        wide = kw_per.pivot_table(
                            index="interval", columns="keyword", values="count", aggfunc="sum"
                        ).fillna(0)

                        if wide.empty:
                            st.info("Not enough keyword data for velocity chart.")
                        else:
                            # Select top 3-5 keywords by total frequency
                            top_keywords = wide.sum(axis=0).sort_values(ascending=False).head(5).index.tolist()
                            top_keywords = [k for k in top_keywords if k in wide.columns]
                            if not top_keywords:
                                st.info("No strong keywords found to plot velocity.")
                            else:
                                small = wide[top_keywords].copy()

                                # smoothing with rolling mean
                                smoothed = small.rolling(window=3, min_periods=1, center=True).mean()

                                # velocity as step changes
                                velocity = smoothed.diff().fillna(0)

                                # normalize each keyword by max abs velocity (plus 1 to avoid division by zero)
                                norm = velocity.copy()
                                for col in norm.columns:
                                    max_val = abs(norm[col]).max()
                                    norm[col] = norm[col] / (max_val + 1)

                                # use the timestamp index as x-axis labels
                                x = list(norm.index.astype(str))

                                fig, ax = plt.subplots(figsize=(11, 5))
                                for kw in norm.columns:
                                    ax.plot(x, norm[kw], linewidth=2, marker="", label=kw)

                                ax.set_title("Trend Velocity (Smoothed Growth Rate)")
                                ax.set_xlabel("Time Interval")
                                ax.set_ylabel("Normalized Velocity")
                                ax.legend(loc="upper left", fontsize=9, ncol=2)

                                # make x-axis readable
                                n_ticks = min(len(x), 8)
                                if n_ticks > 1:
                                    step = max(1, len(x) // n_ticks)
                                    tick_locs = list(range(0, len(x), step))
                                    ax.set_xticks([x[i] for i in tick_locs])
                                ax.tick_params(axis="x", rotation=30, labelsize=8)

                                fig.tight_layout()
                                st.pyplot(fig, clear_figure=True)
                    else:
                        st.info("Not enough time-series data for velocity chart.")
                except Exception as e:
                    st.info(f"Velocity chart unavailable: {e}")

        with st.expander("📊 Activity Insights — Post timing by hour"):
            try:
                from time_analysis import compute_trends_over_time
                _, kw_per2, _ = compute_trends_over_time(
                    df, text_col="text", ts_col="timestamp", interval="hour", top_k=30
                )
            except Exception as e:
                st.warning(f"Could not compute trends: {e}")
                kw_per2 = pd.DataFrame()

            if kw_per2 is None or kw_per2.empty:
                st.info("Not enough data for activity insights.")
            else:
                keyword_order = (
                    kw_per2.groupby("keyword")["count"].sum().sort_values(ascending=False).index.tolist()
                )
                if not keyword_order:
                    st.info("No keywords found for activity insights.")
                else:
                    topic = st.selectbox(
                        "Topic selector",
                        options=keyword_order[:20],
                        index=0,
                        help="Select keyword for per-hour activity insights.",
                        key="activity_topic_select",
                    )

                    view_mode = st.radio(
                        "View mode",
                        options=["Bar Chart", "Heatmap"],
                        index=0,
                        horizontal=True,
                        key="activity_view_mode",
                    )

                    text_col = "clean_text" if "clean_text" in df.columns else "text"
                    mask = df[text_col].astype(str).str.contains(
                        rf"\b{re.escape(topic)}\b", case=False, regex=True, na=False
                    )
                    topic_df = df.loc[mask].copy()

                    if topic_df.empty:
                        st.warning(f"No posts found for topic '{topic}'.")
                    else:
                        topic_df["_dt"] = pd.to_datetime(topic_df["timestamp"], errors="coerce")
                        topic_df = topic_df.dropna(subset=["_dt"])
                        if topic_df.empty:
                            st.warning("No valid timestamps for selected topic.")
                        else:
                            topic_df["hour"] = topic_df["_dt"].dt.hour
                            topic_df["day"] = topic_df["_dt"].dt.strftime("%Y-%m-%d")

                            hourly = (
                                topic_df.groupby("hour").size().reindex(range(24), fill_value=0).reset_index(name="count")
                            )
                            heat_table = (
                                topic_df.groupby(["day", "hour"]).size().reset_index(name="count")
                            )
                            peak_hour = int(hourly.loc[hourly["count"].idxmax(), "hour"])
                            peak_count = int(hourly["count"].max())
                            total_posts = int(len(topic_df))
                            avg_per_hour = float(hourly["count"].mean())

                            card1, card2, card3 = st.columns(3)
                            card1.metric("Peak hour", f"{peak_hour}:00", f"{peak_count} posts")
                            card2.metric("Total posts", f"{total_posts}")
                            card3.metric("Average posts/hour", f"{avg_per_hour:.2f}")

                            st.markdown(
                                f"Most discussions happen around **{peak_hour}:00** with **{peak_count}** posts in one hour."
                            )

                            try:
                                import plotly.express as px

                                hourly["hour_label"] = hourly["hour"].apply(
                                    lambda h: f"{(h%12 or 12)} {'AM' if h<12 else 'PM'}"
                                )

                                if view_mode == "Bar Chart":
                                    bar_fig = px.bar(
                                        hourly,
                                        x="hour_label",
                                        y="count",
                                        title=f"Hourly posts for '{topic}'",
                                        labels={"hour_label": "Hour", "count": "Post Count"},
                                        hover_data={"hour_label": True, "count": True},
                                    )
                                    bar_fig.update_traces(
                                        marker_color=[
                                            "crimson" if h == peak_hour else "steelblue" for h in hourly["hour"]
                                        ]
                                    )
                                    bar_fig.update_layout(xaxis_tickangle=-30)
                                    st.plotly_chart(bar_fig, use_container_width=True)

                                else:
                                    pivot = heat_table.pivot(index="day", columns="hour", values="count").fillna(0)
                                    pivot = pivot.reindex(columns=range(24), fill_value=0)
                                    heat_fig = px.imshow(
                                        pivot,
                                        labels={"x": "Hour", "y": "Day", "color": "Post Count"},
                                        x=[f"{h}:00" for h in pivot.columns],
                                        y=pivot.index,
                                        aspect="auto",
                                        color_continuous_scale="Blues",
                                    )
                                    heat_fig.update_layout(title=f"Daily hour heatmap for '{topic}'")
                                    st.plotly_chart(heat_fig, use_container_width=True)

                            except Exception as e:
                                st.warning(f"Plotly not available or rendered: {e}")

        st.subheader("Top keywords (frequency)")
        if kw_df.empty:
            st.warning("No keywords found after preprocessing.")
        else:
            st.pyplot(plot_bar(kw_df, "keyword", "count", "Top keywords"), clear_figure=True, use_container_width=True)
            st.dataframe(kw_df, use_container_width=True)

        st.subheader("Top hashtags (frequency)")
        if ht_df.empty:
            st.info("No hashtags detected in the dataset.")
        else:
            st.pyplot(plot_bar(ht_df, "hashtag", "count", "Top hashtags"), clear_figure=True, use_container_width=True)
            st.dataframe(ht_df, use_container_width=True)

        st.subheader("Top TF‑IDF terms")
        if tfidf_df.empty:
            st.info("TF‑IDF needs enough repeated terms (min_df=2). Try a larger dataset.")
        else:
            tfidf_show = tfidf_df.copy()
            tfidf_show["score"] = tfidf_show["score"].map(lambda x: float(f"{x:.6f}"))
            st.pyplot(plot_bar(tfidf_show, "term", "score", "Top TF‑IDF terms"), clear_figure=True, use_container_width=True)
            st.dataframe(tfidf_show, use_container_width=True)

        # ── What's Being Discussed (AI Summary) ──────────────────────────────
        st.divider()
        st.subheader("💬 What's Being Discussed")
        st.caption("AI-generated summary of the main themes in the current dataset.")
        if not _HAS_SUMMARY:
            st.info("Summary module not available. Ensure summarizer.py is present.")
        else:
            summarize_col1, summarize_col2 = st.columns([3, 1])
            with summarize_col2:
                if st.button("🔄 Generate Summary", key="trends_summary_btn"):
                    st.session_state["run_summary"] = True
            if st.session_state.get("run_summary"):
                try:
                    snap = generate_discussion_snapshot(df)
                    themes = snap.get("themes", []) or []
                    summary_text = (snap.get("summary") or "").strip()
                    mix = snap.get("sentiment_mix", {}) or {}
                    s1, s2, s3 = st.columns(3)
                    s1.metric("Posts Analysed", str(snap.get("total_posts", len(df))))
                    s2.metric("Top Themes", str(len(themes)))
                    s3.metric("Sentiment Mix", f"+{mix.get('positive',0)}% ={mix.get('neutral',0)}% -{mix.get('negative',0)}%")
                    if themes:
                        st.write("**Themes:**", ", ".join([str(t) for t in themes[:10]]))
                    if summary_text:
                        st.markdown(summary_text)
                    else:
                        st.info("Summary unavailable — try a larger dataset.")
                except Exception as e:
                    st.warning(f"Summary error: {e}")
            else:
                st.info("Click 'Generate Summary' to analyse what's being discussed right now.")


    with tab_topics:
        st.subheader("Discovered topics (LDA)")
        if lda_pack is None:
            st.info(
                "Not enough data for stable LDA topics. Try a bigger dataset or reduce preprocessing strictness / increase posts."
            )
        else:
            lda = lda_pack["lda"]
            tdf = lda_topics_table(lda, num_words=10)
            st.dataframe(tdf, use_container_width=True)

            # Coherence score — academic quality metric
            st.subheader("Topic Coherence Score (c_v)")
            try:
                from gensim.models import CoherenceModel
                with st.spinner("Computing coherence score..."):
                    coherence_model = CoherenceModel(
                        model=lda,
                        texts=lda_pack["filtered_tokens"],
                        dictionary=lda_pack["dictionary"],
                        coherence="c_v",
                    )
                    c_score = coherence_model.get_coherence()
                col_c1, col_c2 = st.columns(2)
                col_c1.metric("Coherence (c_v)", f"{c_score:.4f}")
                col_c2.metric("Interpretation", "Good ✅" if c_score >= 0.4 else "Moderate ⚠️" if c_score >= 0.3 else "Low ❌")
                st.caption(
                    "Coherence (c_v) measures how semantically similar the top words "
                    "within each topic are. Scores > 0.4 indicate meaningful, well-separated topics. "
                    "Use the **LDA passes** and **LDA topics** sliders in the sidebar to optimise."
                )
            except Exception as e:
                st.info(f"Coherence computation unavailable: {e}")

            st.subheader("Topic sentiment (dominant topic per post)")
            filtered_indices = lda_pack["filtered_indices"]
            corpus = lda_pack["corpus"]

            dom_topic = []
            for bow in corpus:
                topics = lda.get_document_topics(bow, minimum_probability=0.0)
                best = max(topics, key=lambda x: x[1])[0] if topics else 0
                dom_topic.append(best)

            topic_labels = [f"Topic {t}" for t in dom_topic]

            filtered_raw = [raw_texts[i] for i in filtered_indices]

            tmp = pd.DataFrame({"text": filtered_raw, "topic": topic_labels})
            tmp = pd.concat([tmp, vader_sentiment(tmp["text"].tolist())], axis=1)

            pick = st.selectbox("Select a topic", options=sorted(tmp["topic"].unique()), index=0)
            tsub = tmp[tmp["topic"] == pick]
            tcounts = tsub["sentiment"].value_counts()
            st.pyplot(plot_pie_sentiment(tcounts, f"Sentiment for: {pick}"), clear_figure=True)
            with st.expander("View posts in this topic"):
                st.dataframe(tsub[["text", "sentiment", "compound"]].head(300), use_container_width=True)


    # Time-Based Trends
    with tab_timebased:
        if "timestamp" in df.columns and _HAS_ADAPTERS:
            try:
                posts_per, kw_per, peak = compute_trends_over_time(
                    df, text_col="text", ts_col="timestamp", interval=time_interval, top_k=5
                )
                if not posts_per.empty:
                    st.subheader("Trends over time")
                    fig, ax = plt.subplots(figsize=(10, 4))
                    ax.plot(posts_per["interval"].astype(str), posts_per["count"], marker="o", markersize=4)
                    ax.set_title(f"Posts per {time_interval}")
                    ax.set_xlabel("Time interval")
                    ax.set_ylabel("Post count")
                    plt.xticks(rotation=45, ha="right")
                    fig.tight_layout()
                    st.pyplot(fig, clear_figure=True)
                    st.subheader("Peak activity")
                    st.info(f"Peak interval: {peak}" if peak else "No peak detected.")
                    rate = trend_growth_rate(posts_per)
                    if rate is not None:
                        st.caption(f"Trend growth rate: {rate:.2%}")
                else:
                    st.warning("Could not compute time-based trends. Timestamps may be unparseable.")
            except Exception as e:
                st.warning(f"Time analysis error: {e}. Check timestamp format.")
        else:
            st.info("Timestamp column needed for time-based trends. Use collected data or CSV with created_at/timestamp.")


    # Geographic Insights
    with tab_geo:
        st.subheader("Geographic Insights")
        try:
            if "location" not in df.columns:
                st.info(
                    "No location data found. Location is extracted from Twitter user profiles \n"
                    "or CSV location columns."
                )
            else:
                loc = df["location"].astype(str)
                loc = loc.replace({"nan": "", "None": ""}).map(lambda x: x.strip())
                loc = loc[loc.str.len() > 0]
                if loc.empty:
                    st.info(
                        "No location data found. Location is extracted from Twitter user profiles \n"
                        "or CSV location columns."
                    )
                else:
                    try:
                        import pycountry
                        import plotly.express as px
                    except Exception as e:
                        st.warning(f"Plotly/PyCountry not available: {e}. Install dependencies to enable this tab.")
                        st.stop()

                    aliases = {
                        "usa": "United States",
                        "u.s.a": "United States",
                        "us": "United States",
                        "u.s.": "United States",
                        "uk": "United Kingdom",
                        "u.k.": "United Kingdom",
                        "uae": "United Arab Emirates",
                    }

                    def map_to_country_name(s: str) -> str | None:
                        try:
                            raw = (s or "").strip()
                            if not raw:
                                return None
                            # pick the most "country-like" chunk
                            chunk = raw.split("|")[0].strip()
                            chunk = chunk.split("-")[-1].strip()
                            if "," in chunk:
                                chunk = chunk.split(",")[-1].strip()
                            key = chunk.lower().strip(".")
                            if key in aliases:
                                return aliases[key]
                            try:
                                c = pycountry.countries.lookup(chunk)
                                return c.name
                            except Exception:
                                pass
                            try:
                                c = pycountry.countries.search_fuzzy(chunk)[0]
                                return c.name
                            except Exception:
                                return None
                        except Exception:
                            return None

                    mapped = loc.map(map_to_country_name).dropna()
                    mapped = mapped[mapped.astype(str).str.len() > 0]
                    if mapped.empty:
                        st.info(
                            "No location data found. Location is extracted from Twitter user profiles \n"
                            "or CSV location columns."
                        )
                    else:
                        country_counts = mapped.value_counts().rename_axis("country").reset_index(name="count")
                        fig = px.choropleth(
                            country_counts,
                            locations="country",
                            locationmode="country names",
                            color="count",
                            color_continuous_scale="Viridis",
                            title="Post/Trend origins by country (inferred)",
                        )
                        fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))
                        st.plotly_chart(fig, use_container_width=True)

                        top10 = country_counts.head(10)
                        bar = px.bar(top10.iloc[::-1], x="count", y="country", orientation="h", title="Top 10 countries")
                        bar.update_layout(margin=dict(l=0, r=0, t=40, b=0))
                        st.plotly_chart(bar, use_container_width=True)
        except Exception:
            st.info(
                "No location data found. Location is extracted from Twitter user profiles \n"
                "or CSV location columns."
            )

    # Subquery Search
    with tab_subquery:
        st.subheader("🔍 Advanced Subquery Search")
        st.caption("Search using boolean operators: term1 term2 (required), -term3 (excluded), |term4 (optional)")
        
        search_col = st.columns([4, 2, 2])
        with search_col[0]:
            search_query = st.text_input(
                "Search query",
                value="trending",
                placeholder="e.g., AI -hype |innovation",
                help="Boolean syntax: required terms, -excluded, |optional"
            )
        with search_col[1]:
            selected_platform = st.selectbox(
                "Platform filter",
                ["All"] + sorted(df["platform"].unique().tolist()) if "platform" in df.columns else ["All"],
                index=0
            )
        with search_col[2]:
            case_sensitive = st.checkbox("Case sensitive")
        
        if search_query.strip():
            try:
                search_engine = SubquerySearch(df)
                results = search_engine.search_and_analyze(
                    query=search_query,
                    top_keywords=10,
                    platform_filter=None if selected_platform == "All" else selected_platform
                )
                
                if results["total_matches"] > 0:
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Matches found", results["total_matches"])
                    c2.metric("Platforms", len(results["platforms"]) if results["platforms"] else 1)
                    c3.metric("Top keywords", len(results["keywords"]) if results["keywords"] else 0)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Platform breakdown")
                        if results["platforms"]:
                            platform_df = pd.DataFrame(
                                list(results["platforms"].items()),
                                columns=["platform", "count"]
                            ).sort_values("count", ascending=False)
                            fig = plt.subplots(figsize=(5, 3))
                            plt.bar(platform_df["platform"], platform_df["count"], color="#4e79a7")
                            plt.xticks(rotation=45, ha="right")
                            plt.title("Posts per platform (search results)")
                            st.pyplot(fig[0], clear_figure=True)
                        else:
                            st.info("No platform breakdown available")
                    
                    with col2:
                        st.subheader("Sentiment breakdown")
                        if results["sentiment"]:
                            sent_series = pd.Series(results["sentiment"])
                            fig, ax = plt.subplots(figsize=(5, 3))
                            colors = {"Positive": "#59a14f", "Neutral": "#bab0ac", "Negative": "#e15759"}
                            ax.pie(
                                sent_series.values,
                                labels=sent_series.index,
                                autopct=lambda p: f"{p:.0f}%",
                                colors=[colors.get(l, "#999999") for l in sent_series.index]
                            )
                            st.pyplot(fig, clear_figure=True)
                        else:
                            st.info("No sentiment breakdown available")
                    
                    st.subheader("Top keywords in results")
                    if results["keywords"]:
                        st.write(", ".join(results["keywords"]))
                    
                    st.subheader("Matching posts")
                    results_to_show = results["results"][["text", "platform"]].copy()
                    if "sentiment" in results_to_show.columns:
                        results_to_show = results_to_show[["text", "platform", "sentiment"]]
                    st.dataframe(results_to_show.head(50), use_container_width=True, height=400)
                    
                    # Export results
                    csv_export = results["results"][["text", "platform"]].to_csv(index=False).encode("utf-8")
                    st.download_button(
                        "📥 Download search results",
                        data=csv_export,
                        file_name=f"search_results_{search_query.replace(' ', '_')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning(f"No results found for query: {search_query}")
                    
                    st.subheader("Suggested searches")
                    search_engine = SubquerySearch(df)
                    suggestions = search_engine.trending_subqueries()
                    if suggestions:
                        st.write("Try one of these:")
                        for suggestion in suggestions[:5]:
                            if st.button(suggestion, key=f"suggest_{suggestion}"):
                                st.rerun()
            except Exception as e:
                st.error(f"Search error: {str(e)}")
        else:
            st.info("Enter a search query to begin. Use boolean operators for advanced searches.")


    # Footer
    st.markdown(
        """
        <style>
        .app-footer { position: fixed; left: 0.75rem; bottom: 0.5rem; font-size: 0.8rem; color: #6b7280; z-index: 9999; }
        </style>
        <div class="app-footer">Crafted with ❤️ by jaswanth nanneboyina</div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()

