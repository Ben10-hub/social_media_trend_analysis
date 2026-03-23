# Real-Time Trending Topics Analyzer - Enhanced Version

## 🎯 Project Overview
This project identifies real-time trending topics from multiple social media platforms, providing comprehensive sentiment analysis, geographic insights, and advanced search capabilities.

## 🆕 New Features Added

### 1. **YouTube Scraping** 📺
- **Quick YouTube (No API)**: Search YouTube videos by keywords using RSS feeds
- **Fetch YouTube (API)**: Get trending videos by region using Google YouTube API v3
- Located in: [adapters/youtube_adapter.py](adapters/youtube_adapter.py)

**Usage:**
```python
from adapters.youtube_adapter import quick_youtube_scrape, fetch_youtube_trending

# Without API key
df, err = quick_youtube_scrape(query="trending technology", limit=30)

# With YouTube API key
df, err = fetch_youtube_trending(max_results=50, region_code="US")
```

### 2. **Instagram Scraping** 📸
- **Quick Instagram (No API)**: Search Instagram posts by hashtags
- **Fetch Instagram (API)**: Get trending content using Meta Graph API
- Located in: [adapters/instagram_adapter.py](adapters/instagram_adapter.py)

**Usage:**
```python
from adapters.instagram_adapter import quick_instagram_scrape, fetch_instagram_trending

# Without API key (hashtag search)
df, err = quick_instagram_scrape(hashtag="trending", limit=30)

# With Instagram API token
df, err = fetch_instagram_trending(max_results=50)
```

### 3. **Global Trending Topics** 🌍
- Collect trending posts from **all platforms simultaneously** (Reddit, Twitter, YouTube, Instagram)
- Automatic platform detection and topic extraction
- Real-time global trending summary
- Located in: [global_trends.py](global_trends.py)

**Features:**
- Multi-platform trend aggregation
- Top keywords extraction per platform
- Time-range aware trending
- Error handling with graceful fallbacks

**Usage:**
```python
from global_trends import collect_global_trending, get_trending_summary

# Collect from all platforms
combined_df, info = collect_global_trending(
    include_reddit=True,
    include_twitter=True,
    include_youtube=True,
    include_instagram=True,
    posts_per_source=50
)

# Get trending summary
summary = get_trending_summary(combined_df)
print(f"Global keywords: {summary['top_keywords']}")
print(f"Platforms: {summary['platforms']}")
```

### 4. **Advanced Subquery Search** 🔍
- Complex boolean search with multiple operators
- Platform-based filtering
- Date range filtering
- Faceted search results
- Located in: [subquery_search.py](subquery_search.py)

**Search Syntax:**
- `term1 term2` - Both terms required
- `-term3` - Exclude this term
- `|term4` - Optional term (boosts relevance)

**Examples:**
- `AI -hype` - Posts about AI but not hype
- `trending |viral |popular` - Trending with optional viral/popular keywords
- `machine learning -basics` - Advanced ML topics

**Usage:**
```python
from subquery_search import SubquerySearch

search = SubquerySearch(df)

# Simple search
results = search.search(query="AI -hype", platform_filter="reddit")

# Advanced analysis with stats
analysis = search.search_and_analyze(
    query="trending technology",
    top_keywords=15,
    platform_filter=None
)

# Faceted search
platforms = search.faceted_search(query="AI", facet_by="platform")
```

### 5. **Geographic Insights Enhancement** 🗺️
- Sample data with location fields included
- Support for multiple location formats
- Country mapping visualization
- Enhanced sample dataset: [sample_social_posts_with_location.csv](data/sample_social_posts_with_location.csv)

**Features:**
- Automatic location parsing
- Country-level choropleth maps
- Top countries bar charts
- Location aliases (USA, US, U.S., etc.)

## 📊 Data Sources

The application now supports:

| Source | Quick (No API) | Fetch (API) | Status |
|--------|---|---|--------|
| Reddit | ✅ Quick Reddit | ✅ Fetch Reddit | Fully Supported |
| Twitter/X | ✅ Quick X (Nitter) | ✅ Fetch Twitter | Fully Supported |
| YouTube | ✅ Quick YouTube | ✅ Fetch YouTube | **NEW** |
| Instagram | ✅ Quick Instagram | ✅ Fetch Instagram | **NEW** |
| CSV Upload | ✅ Upload CSV | - | Supported |
| Global Trending | ✅ All Platforms | Multi-API | **NEW** |

## 🚀 Quick Start

### Installation

```bash
# Clone repository
cd proj_2\ copy\ 3

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install additional packages for new features
pip install google-api-python-client instagrapi feedparser plotly pycountry
```

### Environment Variables

Create a `.env` file with optional API keys:

```env
# Reddit API (optional)
REDDIT_CLIENT_ID=your_id
REDDIT_CLIENT_SECRET=your_secret
REDDIT_USER_AGENT=TrendAnalyzer/1.0

# Twitter API v2 (optional)
TWITTER_BEARER_TOKEN=your_bearer_token

# YouTube API v3 (optional)
YOUTUBE_API_KEY=your_api_key

# Instagram API (optional)
INSTAGRAM_ACCESS_TOKEN=your_access_token

# RapidAPI (optional)
RAPIDAPI_KEY=your_rapidapi_key
```

### Running the Application

```bash
# Run main Streamlit app
streamlit run app.py

# Collect real-time trends
python collect_real_time.py

# Quick demo
python test_reddit.py
```

## 📈 Key Tabs in Dashboard

1. **Overview** - Sentiment distribution & word clouds
2. **Trends** - Keywords, hashtags, TF-IDF terms
3. **Sentiment** - Per-trend sentiment analysis
4. **Topics (LDA)** - Topic modeling & discovery
5. **Real-Time Insights** - Live metrics & platform distribution
6. **Time-Based Trends** - Growth rate & peak activity
7. **Platform Comparison** - Cross-platform analysis
8. **Geographic Insights** - **NEW** World map with post origins
9. **🔍 Subquery Search** - **NEW** Advanced boolean search
10. **💬 What's Being Discussed** - AI-powered summaries

## 💾 Database & Storage

- **SQLite Database**: Persistent storage of collected posts
- **CSV Export**: Export analysis results to CSV
- **Sample Data**: Pre-loaded datasets for testing
- **Location Data**: Automatic geographic tagging

## 🔧 Advanced Features

### Trend Detection
```python
from alert_engine import detect_keyword_spikes

spikes = detect_keyword_spikes(df, window=5, spike_multiplier=2.0)
```

### Time Series Analysis
```python
from time_analysis import compute_trends_over_time, trend_growth_rate

posts_per, kw_per, peak = compute_trends_over_time(
    df, 
    text_col="text", 
    ts_col="timestamp", 
    interval="hour"
)
```

### AI-Powered Summaries
```python
from summarizer import generate_discussion_snapshot

snapshot = generate_discussion_snapshot(df)
print(snapshot['themes'])  # Top themes discussed
print(snapshot['summary'])  # AI-generated summary
```

## 📊 Sample Output

### Global Trending
```
Total posts collected: 1,250
Platforms: reddit (300), twitter (400), youtube (300), instagram (250)

Top Keywords:
- AI: 145 mentions
- trending: 98 mentions
- technology: 87 mentions
- innovation: 76 mentions
```

### Subquery Search Example
```
Query: "AI -hype"
Matches: 342
Platforms: reddit (120), twitter (180), youtube (42)
Sentiment: 45% positive, 35% neutral, 20% negative
```

### Geographic Distribution
```
United States: 250 posts (20%)
India: 180 posts (14.4%)
United Kingdom: 120 posts (9.6%)
Australia: 95 posts (7.6%)
Canada: 85 posts (6.8%)
```

## 🔐 Security Notes

- Never commit `.env` files with API keys
- Use RapidAPI for public API access when available
- Respect rate limits of each platform
- Check platform ToS for scraping restrictions

## 📚 Dependencies

Key packages:
- `streamlit` - Web UI framework
- `pandas` - Data manipulation
- `nltk` - Natural Language Processing
- `gensim` - Topic modeling (LDA)
- `scikit-learn` - Machine learning
- `feedparser` - RSS parsing
- `requests` - HTTP library
- `tweepy` - Twitter/X API
- `praw` - Reddit API
- `google-api-python-client` - YouTube API
- `instagrapi` - Instagram API
- `plotly` - Interactive visualizations
- `pycountry` - Country mapping

## 🐛 Troubleshooting

### No YouTube results
- Check YouTube API key configuration
- Verify RSS feed access if using Quick YouTube
- Region code may restrict results

### Instagram scraping blocked
- Instagram has strict anti-scraping measures
- Consider using Meta Graph API with access token
- Implement delays between requests

### Missing location data
- Only Twitter provides location in structured format
- Upload CSV with location column for geographic analysis
- Use the enhanced sample dataset

## 📝 Contributing

To add new data sources:
1. Create adapter in `adapters/` directory
2. Implement `to_unified_df()` from base.py
3. Add to imports in `app.py`
4. Add to data source radio options
5. Implement data loading logic

## 📄 License

MIT License - Feel free to use and modify

## 👤 Author

Crafted by **jaswanth nanneboyina**

## 🎯 Future Enhancements

- [ ] TikTok API integration
- [ ] Streaming data pipeline
- [ ] Real-time alerts & notifications
- [ ] Prediction models for trend forecasting
- [ ] Multi-language support
- [ ] Advanced NLP (NER, dependency parsing)
- [ ] Graph visualization for topic connections

---

**Last Updated**: March 18, 2026
