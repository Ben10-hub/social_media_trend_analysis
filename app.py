import io
import os
import re
import string
from collections import Counter
from pathlib import Path

# Ensure Matplotlib uses a writable config/cache directory in restricted environments.
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

# Optional: adapters and data store for multi-platform / real-time features
try:
    from adapters.csv_adapter import load_csv_unified
    from adapters.reddit_adapter import fetch_reddit_posts
    from adapters.twitter_adapter import fetch_twitter_posts
    from data_store import append_posts, get_db_path, load_all_posts
    from time_analysis import compute_trends_over_time, trend_growth_rate
    _HAS_ADAPTERS = True
except ImportError:
    _HAS_ADAPTERS = False


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


def apply_theme(dark: bool):
    if not dark:
        return
    st.markdown(
        """
        <style>
        .stApp { background: #0b1220; color: #e5e7eb; }
        h1, h2, h3, h4 { color: #e5e7eb; }
        section[data-testid="stSidebar"] { background: #0f172a; }
        div[data-testid="stMetricValue"] { color: #e5e7eb; }
        </style>
        """,
        unsafe_allow_html=True,
    )


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

    with st.sidebar:
        st.title("Controls")
        st.caption("Choose data source or upload a CSV with a text column.")
        dark_mode = st.toggle("Dark mode", value=False)
        apply_theme(dark_mode)

        top_n = st.slider("Number of trends", min_value=5, max_value=50, value=15, step=1)
        lda_topics_n = st.slider("LDA topics", min_value=2, max_value=12, value=5, step=1)
        lda_passes = st.slider("LDA passes", min_value=5, max_value=30, value=10, step=1)
        time_interval = st.selectbox("Time grouping", options=["hour", "minute"], index=0)

        data_source = st.radio(
            "Data source",
            ["Sample", "Upload CSV", "Load from collected", "Fetch Reddit", "Fetch Twitter"],
            index=0,
        )
        uploaded = st.file_uploader("Upload CSV", type=["csv"]) if data_source == "Upload CSV" else None

    st.title("Hybrid Social Media Trend & Sentiment Analysis")
    st.caption("Trends (hashtags/keywords/TF‑IDF/LDA) + Sentiment (VADER) + Real-time & time-based analytics.")

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
        if uploaded is not None:
            try:
                if _HAS_ADAPTERS:
                    df = load_csv_unified(file_bytes=uploaded.getvalue(), platform_default="csv")
                else:
                    df = load_csv(uploaded.getvalue())
                    df["platform"] = "csv"
                    df["timestamp"] = pd.Timestamp.utcnow().isoformat()
                    text_col = infer_text_column([c for c in df.columns if df[c].dtype == "object"] or list(df.columns))
                    if text_col:
                        df["text"] = df[text_col].astype(str)
            except Exception as e:
                err_msg = str(e)
        else:
            st.info("Upload a CSV file.")
            st.stop()
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
    elif data_source == "Fetch Reddit":
        if _HAS_ADAPTERS:
            with st.spinner("Fetching from Reddit..."):
                df, err = fetch_reddit_posts(subreddits=["python", "technology"], limit_per_sub=30)
            if err:
                st.warning(f"Reddit API: {err}. Using sample dataset.")
                sample_path = Path(__file__).resolve().parent / "data" / "sample_social_posts.csv"
                df = load_csv_unified(file_path=str(sample_path), platform_default="sample")
            elif df is None or df.empty:
                st.warning("No Reddit posts returned. Using sample dataset.")
                sample_path = Path(__file__).resolve().parent / "data" / "sample_social_posts.csv"
                df = load_csv_unified(file_path=str(sample_path), platform_default="sample")
        else:
            st.warning("Reddit adapter not available. Use sample or upload.")
            st.stop()
    elif data_source == "Fetch Twitter":
        if _HAS_ADAPTERS:
            with st.spinner("Fetching from Twitter..."):
                df, err = fetch_twitter_posts(query="AI OR machine learning", max_results=50)
            if err:
                st.warning(f"Twitter API: {err}. Using sample dataset.")
                sample_path = Path(__file__).resolve().parent / "data" / "sample_social_posts.csv"
                df = load_csv_unified(file_path=str(sample_path), platform_default="sample")
            elif df is None or df.empty:
                st.warning("No tweets returned. Using sample dataset.")
                sample_path = Path(__file__).resolve().parent / "data" / "sample_social_posts.csv"
                df = load_csv_unified(file_path=str(sample_path), platform_default="sample")
        else:
            st.warning("Twitter adapter not available. Use sample or upload.")
            st.stop()

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
            if st.button("Collect Now", help="Fetch Reddit posts and append to SQLite"):
                with st.spinner("Fetching..."):
                    rdf, err = fetch_reddit_posts(subreddits=["python", "technology"], limit_per_sub=25)
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

    with st.expander("Dataset preview", expanded=True):
        st.dataframe(df.head(30), use_container_width=True)
        st.caption(f"Rows: {len(df):,} | Columns: {len(df.columns)}")

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

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Posts", f"{len(df):,}")
    c2.metric("Unique keywords", f"{len(set([t for toks in tokens_list for t in toks])):,}")
    c3.metric("Unique hashtags", f"{len(set([h for hs in df['hashtags'] for h in hs])):,}")
    c4.metric("Avg sentiment (compound)", f"{df['compound'].mean():.3f}")

    tab_overview, tab_trends, tab_sentiment, tab_topics, tab_realtime, tab_timebased, tab_platform = st.tabs([
        "Overview", "Trends", "Sentiment", "Topics (LDA)",
        "Real-Time Insights", "Time-Based Trends", "Platform Comparison",
    ])

    with tab_overview:
        st.subheader("Overall sentiment")
        counts = df["sentiment"].value_counts()
        fig = plot_pie_sentiment(counts, "Overall sentiment distribution")
        st.pyplot(fig, clear_figure=True, use_container_width=False)

        st.subheader("Word cloud (frequent terms)")
        wc_fig = make_wordcloud(tokens_list)
        if wc_fig is None:
            st.warning("Not enough processed text to build a word cloud.")
        else:
            st.pyplot(wc_fig, clear_figure=True, use_container_width=True)

    with tab_trends:
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

    with tab_sentiment:
        st.subheader("Sentiment per trend")
        trend_mode = st.radio("Trend type", ["Keyword", "Hashtag", "TF‑IDF term"], horizontal=True)

        if trend_mode == "Keyword":
            options = kw_df["keyword"].tolist() if not kw_df.empty else []
        elif trend_mode == "Hashtag":
            options = ht_df["hashtag"].tolist() if not ht_df.empty else []
        else:
            options = tfidf_df["term"].tolist() if not tfidf_df.empty else []

        if not options:
            st.info("No trends available to analyze.")
        else:
            selected = st.selectbox("Select a trend", options=options, index=0)

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

                dist = (
                    subset["sentiment"]
                    .value_counts(normalize=True)
                    .reindex(["Positive", "Neutral", "Negative"])
                    .fillna(0.0)
                    .rename("share")
                    .reset_index()
                    .rename(columns={"index": "sentiment"})
                )
                dist["share"] = dist["share"].map(lambda x: float(f"{x:.3f}"))
                st.dataframe(dist, use_container_width=True)

                with st.expander("View matching posts"):
                    st.dataframe(subset[["text", "sentiment", "compound"]].head(200), use_container_width=True)

        st.subheader("Download results")
        out = df[["text", "sentiment", "compound", "clean_text"]].copy()
        out_csv = out.to_csv(index=False).encode("utf-8")
        st.download_button("Download sentiment results CSV", data=out_csv, file_name="sentiment_results.csv", mime="text/csv")

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

    # Real-Time Insights
    with tab_realtime:
        st.subheader("Live post counter")
        st.metric("Total posts", f"{len(df):,}")
        st.subheader("Latest trending topics")
        if kw_df.empty:
            st.info("Not enough data to show trends.")
        else:
            st.dataframe(kw_df.head(10), use_container_width=True)
        st.subheader("Platform distribution")
        if "platform" in df.columns:
            platform_counts = df["platform"].value_counts()
            fig, ax = plt.subplots(figsize=(6, 3))
            ax.bar(platform_counts.index.astype(str), platform_counts.values, color="#4e79a7")
            ax.set_title("Posts per platform")
            ax.set_xlabel("Platform")
            ax.set_ylabel("Count")
            fig.tight_layout()
            st.pyplot(fig, clear_figure=True)
        else:
            st.info("Platform column not available for this dataset.")

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

    # Platform Comparison
    with tab_platform:
        if "platform" in df.columns and len(df["platform"].unique()) > 1:
            st.subheader("Trends by platform")
            for plat in df["platform"].unique():
                sub = df[df["platform"] == plat]
                st.caption(f"**{plat}** — {len(sub):,} posts")
                if len(sub) > 0:
                    _, sub_tokens = preprocess_texts(sub["text"].tolist())
                    sub_kw = compute_keyword_frequency(sub_tokens, min(5, top_n))
                    if not sub_kw.empty:
                        st.dataframe(sub_kw, use_container_width=True, height=120)
            st.subheader("Sentiment by platform")
            if "sentiment" in df.columns:
                pivot = df.groupby("platform")["sentiment"].value_counts(normalize=True).unstack(fill_value=0)
                fig, ax = plt.subplots(figsize=(8, 4))
                pivot.plot(kind="bar", ax=ax, color={"Positive": "#59a14f", "Neutral": "#bab0ac", "Negative": "#e15759"})
                ax.set_title("Sentiment share by platform")
                ax.set_xlabel("Platform")
                ax.legend(title="Sentiment")
                plt.xticks(rotation=45, ha="right")
                fig.tight_layout()
                st.pyplot(fig, clear_figure=True)
        else:
            st.info("Need multiple platforms for comparison. Use collected data or merge CSVs from different sources.")

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

