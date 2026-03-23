# Hybrid Social Media Trend & Sentiment Analysis Dashboard

A comprehensive **real-time social media analytics platform** built with Streamlit and advanced NLP, featuring trend detection, sentiment analysis, and interactive visualizations.

## ✨ Key Features

### 🎯 Core Analytics
- **Trend Detection**: Hashtags, keyword frequency, TF-IDF, LDA topics with coherence scoring
- **Sentiment Analysis**: VADER sentiment (Positive/Neutral/Negative) with optional TextBlob comparison
- **Multi-Platform Support**: Reddit, X (Twitter), YouTube, Instagram, Hacker News, RSS feeds
- **Time-Based Analysis**: Hourly/minute grouping, peak activity detection, trend velocity

### 📊 Advanced Visualizations
- **Trend Velocity**: Smoothed growth rate charts showing rising/falling keyword trends
- **Activity Insights**: Interactive hourly post timing analysis with bar charts and heatmaps
- **Live Mode**: Auto-refresh dashboard with configurable intervals (10-120 seconds)
- **Geographic Mapping**: World map visualization with country-level insights

### 🔧 Data Sources
- **Sample Dataset**: Built-in sample data for testing
- **CSV Upload**: Custom dataset import with automatic column detection
- **Quick Scrapers**: No-API scraping for Reddit, X, YouTube, Instagram
- **News Sources**: Hacker News and RSS feeds (TechCrunch, BBC, etc.)
- **Collected Data**: SQLite database with historical posts

### 🎛️ Interactive Features
- **Boolean Search**: Advanced query syntax with operators (`-exclude`, `|optional`)
- **Topic Modeling**: LDA with coherence metrics and topic sentiment analysis
- **Real-Time Collection**: Sidebar buttons for instant data fetching
- **AI Summary**: Automated discussion theme extraction

## 🚀 Quick Start

```bash
# Clone and setup
git clone https://github.com/Ben10-hub/social_media_trend_analysis.git
cd social_media_trend_analysis

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

## 📁 Project Structure

```
├── app.py                    # Main Streamlit application
├── adapters/                 # Data source adapters
│   ├── base.py              # Unified data schema
│   ├── reddit_adapter.py    # Reddit API integration
│   ├── twitter_adapter.py   # X/Twitter API integration
│   ├── youtube_adapter.py   # YouTube scraping & API
│   ├── instagram_adapter.py # Instagram scraping & API
│   └── csv_adapter.py       # CSV processing utilities
├── data/                    # Sample datasets
├── data_store.py           # SQLite database operations
├── time_analysis.py        # Time-based trend analysis
├── summarizer.py           # AI discussion summarization
├── subquery_search.py      # Advanced boolean search
├── global_trends.py        # Multi-platform trend aggregation
├── collect_real_time.py    # Background data collection
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🎮 Usage Guide

### 1. Data Source Selection
Choose from multiple data sources in the sidebar:
- **Sample**: Test with built-in dataset
- **Upload CSV**: Import your own data
- **Quick Sources**: No-API scraping (Reddit, X, YouTube, Instagram)
- **News**: Hacker News or RSS feeds
- **Collected**: Load from SQLite database

### 2. Real-Time Collection
Use sidebar buttons to fetch fresh data:
- **Collect Reddit/YouTube/Instagram**: Fetch trending content
- **Live Mode**: Enable auto-refresh (10-120 second intervals)

### 3. Analysis Tabs
- **📊 Overview**: Metrics, sentiment distribution, word clouds
- **📈 Trends**: Keywords, hashtags, TF-IDF, trend velocity
- **🧠 Topics**: LDA topic modeling with coherence scores
- **⏱️ Time Trends**: Activity insights with interactive charts
- **🌍 Geographic**: Location-based analysis and mapping
- **🔍 Search**: Boolean query search with filters

## 🔑 API Configuration (Optional)

### Reddit API
```bash
# Create app at https://www.reddit.com/prefs/apps
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=TrendSentimentApp/1.0
```

### YouTube API
```bash
# Get key from Google Cloud Console
YOUTUBE_API_KEY=your_api_key
```

### Instagram API
```bash
# Meta Graph API token
INSTAGRAM_ACCESS_TOKEN=your_access_token
```

### X (Twitter) API
```bash
# Twitter Developer Portal
TWITTER_BEARER_TOKEN=your_bearer_token
```

## 🆕 Recent Updates (March 2026)

### ✨ New Features
- **Trend Velocity Module**: True growth rate visualization with smoothing
- **Activity Insights**: Interactive hourly analysis with bar/heatmap views
- **Live Mode**: Auto-refresh dashboard with configurable intervals
- **Enhanced Adapters**: Improved YouTube and Instagram scraping

### 🔧 Improvements
- Fixed missing function imports for quick scrapers
- Consolidated tab structure for better UX
- Added comprehensive error handling and fallbacks
- Improved documentation and setup guides

### 📊 Enhanced Analytics
- Topic coherence scoring for LDA models
- VADER vs TextBlob sentiment comparison
- Peak activity detection and metrics
- Interactive Plotly visualizations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Troubleshooting

### Common Issues
- **Import Errors**: Ensure all dependencies are installed
- **API Failures**: Check `.env` configuration and API limits
- **Empty Results**: Try different search terms or data sources
- **Performance**: Use Live Mode sparingly or increase refresh intervals

### Getting Help
- Check the [Quick Start Guide](QUICKSTART.md) for detailed setup
- Review [Features Documentation](FEATURES.md) for advanced usage
- See [Startup Guide](STARTUP.md) for configuration tips

---

**Built with ❤️ using Streamlit, NLTK, scikit-learn, and Plotly**

- **Text processing**: tokenization, cleaning, stopword removal, and lemmatization (implemented in `safe_word_tokenize`, `basic_clean`, and `tokenize_lemmatize`) — see [app.py](app.py).
- **Keyword & hashtag frequency**: counting with Python `Counter` and `most_common` (used in `compute_keyword_frequency`, `compute_hashtag_frequency`) — see [app.py](app.py) and per-interval counts in [time_analysis.py](time_analysis.py).
- **TF‑IDF ranking**: `TfidfVectorizer` to score and rank terms (`compute_tfidf_top_terms`) — see [app.py](app.py).
- **Topic modeling (LDA)**: Gensim dictionary/corpus pipeline and `LdaModel` (`compute_lda_topics`) — see [app.py](app.py).
- **Sentiment analysis**: VADER rule-based sentiment scoring (`vader_sentiment`) — see [app.py](app.py).
- **Time-series trend analysis**: timestamp parsing, hourly/minute bucketing, posts-per-interval aggregation, peak detection, and simple growth-rate (`compute_trends_over_time`, `trend_growth_rate`) — see [time_analysis.py](time_analysis.py).
- **Storage & deduplication**: SQLite with UNIQUE(platform, text) and `INSERT OR IGNORE` to avoid duplicates (`append_posts`, `load_all_posts`) — see [data_store.py](data_store.py).
- **CSV adapter heuristics**: inference of text/timestamp/platform columns and normalization (`load_csv_unified`, `infer_column`) — see [adapters/csv_adapter.py](adapters/csv_adapter.py).
- **API ingestion patterns**: batched loops and rate-aware fetching for Reddit/Twitter adapters (`fetch_reddit_posts`, `fetch_twitter_posts`) — see [adapters/reddit_adapter.py](adapters/reddit_adapter.py) and [adapters/twitter_adapter.py](adapters/twitter_adapter.py).

If you want, I can expand each bullet with example inputs/outputs or add a dedicated `ALGORITHMS.md` file.
