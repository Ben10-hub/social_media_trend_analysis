# Hybrid Social Media Trend & Sentiment Analysis (Streamlit + NLP)

Academic ML/NLP dashboard with **real-time data ingestion**, **time-based trend detection**, and **multi-platform support**.

## Features
- **Trend detection**: hashtags, keyword frequency, TF‑IDF, LDA topics
- **Sentiment**: VADER (Positive / Neutral / Negative)
- **Multi-platform**: CSV upload, Reddit (PRAW), Twitter (Tweepy), SQLite collected data
- **Real-time**: Collect Now button, scheduled collection script
- **Time-based**: hourly/minute grouping, peak activity, trend growth rate
- **Dashboard**: Overview, Trends, Sentiment, Topics (LDA), Real-Time Insights, Time-Based Trends, Platform Comparison

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
