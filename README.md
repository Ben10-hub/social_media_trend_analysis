# Hybrid Social Media Trend & Sentiment Analysis (Streamlit + NLP)

Academic ML/NLP dashboard with **real-time data ingestion**, **time-based trend detection**, and **multi-platform support**.

## Features
- **Trend detection**: hashtags, keyword frequency, TF‑IDF, LDA topics + topic coherence (c_v)
- **Sentiment**: VADER (Positive / Neutral / Negative), with optional TextBlob comparison
- **Multi-source data**: Sample, Upload CSV, Quick Reddit, Quick X, Quick YouTube, Quick Instagram, Hacker News, News RSS, Load from collected
- **Time-based**: hourly/minute grouping, peak activity, trend growth rate, trend velocity
- **Dashboard**: Overview, Trends, Topics (LDA), Time Trends, Geographic, Search
- **Build quality**: fallback to sample on failures, graceful API/error handling

## Files
- `app.py`: Streamlit application
- `adapters/`: Reddit, Twitter, CSV adapters (unified schema: platform | text | timestamp)
- `data_store.py`: SQLite append/dedup
- `time_analysis.py`: Time-based trend analysis
- `collect_real_time.py`: Standalone scheduled collection script
- `data/sample_social_posts.csv`: Sample dataset
- `.env.example`: API credentials template

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

---

## Notes since refactor (March 2026)
- Removed API-only sources from sidebar: `Fetch Reddit`, `Fetch Twitter`, `Fetch YouTube`, `Fetch Instagram`, `Global Trending`.
- Added lightweight no-API sources: `Quick Reddit`, `Quick X`, `Quick YouTube`, `Quick Instagram`.
- Added free sources: `Hacker News`, `News RSS`.
- Merged `Sentiment`, `Real-Time Insights`, `Platform Comparison`, `What’s Being Discussed` into Overview/Trends/Topics tabs.
- Added chart & analysis updates: Trend Velocity, VADER vs TextBlob, Topic Coherence (c_v), Dataset overview metrics.

## API credentials (optional)

### Reddit (for Fetch Reddit and Collect Now)
1. Go to [Reddit Apps](https://www.reddit.com/prefs/apps)
2. Create app (script type)
3. Copy **client id** (under app name) and **secret**
4. Create `.env` in project root:
   ```
   REDDIT_CLIENT_ID=your_client_id
   REDDIT_CLIENT_SECRET=your_client_secret
   REDDIT_USER_AGENT=TrendSentimentApp/1.0
   ```
5. Store securely — never commit `.env` to git.

### Twitter (optional)
1. [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Create project and app, get **Bearer token**
3. Add to `.env`:
   ```
   TWITTER_BEARER_TOKEN=your_bearer_token
   ```

If APIs are not configured, the app falls back to the sample dataset.

---

## Real-time collection
- **Collect Now** (sidebar): Fetches Reddit posts and appends to SQLite. Duplicates are removed.
- **Load from collected**: Use data stored at `data/social_data.db`
- **Scheduled collection**: Run in a separate terminal:
  ```bash
  python collect_real_time.py
  ```
  Fetches Reddit every 5 minutes (configurable via `COLLECT_INTERVAL_MIN` in `.env`). Data is stored in `data/social_data.db`.

---

## Time-based analysis
- Requires `timestamp` column (e.g. `created_at` in sample CSV or collected data).
- **Time grouping**: hour or minute (sidebar).
- **Output**: line chart of posts per interval, peak activity time, trend growth rate.

---

## Error handling
- API fails → sample dataset used
- Empty Reddit/Twitter results → sample dataset used
- No collected data → sample dataset used
- Invalid timestamps → time-based section shows warning

---

## Dataset format
Upload CSV with at least:
- `text`: social media post text

Optional for time-based / platform features:
- `timestamp` or `created_at`
- `platform` or `source`

**Algorithms used**

- **Text processing**: tokenization, cleaning, stopword removal, and lemmatization (implemented in `safe_word_tokenize`, `basic_clean`, and `tokenize_lemmatize`) — see [app.py](app.py).
- **Keyword & hashtag frequency**: counting with Python `Counter` and `most_common` (used in `compute_keyword_frequency`, `compute_hashtag_frequency`) — see [app.py](app.py) and per-interval counts in [time_analysis.py](time_analysis.py).
- **TF‑IDF ranking**: `TfidfVectorizer` to score and rank terms (`compute_tfidf_top_terms`) — see [app.py](app.py).
- **Topic modeling (LDA)**: Gensim dictionary/corpus pipeline and `LdaModel` (`compute_lda_topics`) — see [app.py](app.py).
- **Sentiment analysis**: VADER rule-based sentiment scoring (`vader_sentiment`) — see [app.py](app.py).
- **Time-series trend analysis**: timestamp parsing, hourly/minute bucketing, posts-per-interval aggregation, peak detection, and simple growth-rate (`compute_trends_over_time`, `trend_growth_rate`) — see [time_analysis.py](time_analysis.py).
- **Storage & deduplication**: SQLite with UNIQUE(platform, text) and `INSERT OR IGNORE` to avoid duplicates (`append_posts`, `load_all_posts`) — see [data_store.py](data_store.py).
- **CSV adapter heuristics**: inference of text/timestamp/platform columns and normalization (`load_csv_unified`, `infer_column`) — see [adapters/csv_adapter.py](adapters/csv_adapter.py).
- **API ingestion patterns**: batched loops and rate-aware fetching for Reddit/Twitter adapters (`fetch_reddit_posts`, `fetch_twitter_posts`) — see [adapters/reddit_adapter.py](adapters/reddit_adapter.py) and [adapters/twitter_adapter.py](adapters/twitter_adapter.py).


