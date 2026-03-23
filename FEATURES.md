# 🚀 Advanced Features Documentation

## Overview

This enhanced social media analytics platform includes cutting-edge features for comprehensive trend analysis, real-time monitoring, and interactive data exploration.

## 🎯 Core Features

### 1. **Trend Velocity Analysis** 📈
**Location**: `app.py` - Time Trends tab

**What it does**:
- Calculates true growth rates of keyword usage over time
- Shows which topics are rising vs. falling in popularity
- Provides early detection of emerging trends

**Technical details**:
- Pivots keyword counts to wide format (time × keywords)
- Applies rolling mean smoothing (window=3)
- Computes velocity as first derivative (diff)
- Normalizes by max absolute value for comparability
- Displays top 3-5 keywords only for clarity

**Usage**:
```python
# Automatically computed in Time Trends tab
# Shows normalized velocity chart with clean x-axis
```

### 2. **Interactive Activity Insights** ⏰
**Location**: `app.py` - Time Trends tab

**What it does**:
- Analyzes posting patterns by hour of day
- Interactive topic selector with top keywords
- Dual visualization modes: Bar Chart and Heatmap
- Peak activity detection with metrics cards

**Features**:
- **Topic Selector**: Dropdown with most frequent keywords
- **View Toggle**: Switch between bar chart and daily heatmap
- **Insight Cards**: Peak hour, total posts, average per hour
- **Smart Filtering**: Regex-based keyword matching
- **Plotly Integration**: Hover tooltips and interactive elements

**Usage**:
```python
# In Time Trends tab → Activity Insights expander
# Select topic → Choose view mode → See hourly patterns
```

### 3. **Live Mode Auto-Refresh** 🔄
**Location**: `app.py` - Sidebar controls

**What it does**:
- Automatically refreshes dashboard at configurable intervals
- Re-fetches data from selected source without manual clicks
- Maintains current query parameters and settings

**Technical implementation**:
- Session state tracking to prevent infinite loops
- Configurable refresh interval (10-120 seconds)
- Safe data reloading with fallback handling
- Status indicator showing current mode and last update

**Usage**:
```python
# Sidebar: Enable "Live Mode" checkbox
# Set refresh interval slider (10-120s)
# Status shows at top: "🟢 Live Mode Active"
```

### 4. **Enhanced Data Adapters** 🔌

#### YouTube Adapter (`adapters/youtube_adapter.py`)
```python
# Quick scraping (no API)
df, err = quick_youtube_scrape(query="trending", limit=30)

# API integration (with YOUTUBE_API_KEY)
df, err = fetch_youtube_trending(max_results=50, region_code="US")
```

#### Instagram Adapter (`adapters/instagram_adapter.py`)
```python
# Quick scraping (no API)
df, err = quick_instagram_scrape(hashtag="trending", limit=30)

# API integration (with INSTAGRAM_ACCESS_TOKEN)
df, err = fetch_instagram_trending(max_results=50)
```

### 5. **Advanced Boolean Search** 🔍
**Location**: `subquery_search.py`

**Syntax**:
- `term1 term2` - Both terms required (AND)
- `-term3` - Exclude term (NOT)
- `|term4` - Optional term (OR, boosts relevance)

**Examples**:
```python
# Search for AI content excluding hype
query = "AI -hype"

# Find trending content, boost if viral
query = "trending |viral |popular"

# Advanced topics only
query = "machine learning -basics"
```

### 6. **Multi-Platform Trend Aggregation** 🌍
**Location**: `global_trends.py`

**Capabilities**:
- Simultaneous collection from all platforms
- Cross-platform keyword analysis
- Time-aware trending detection
- Platform-specific insights

**Usage**:
```python
from global_trends import collect_global_trending

# Collect from all platforms
df, info = collect_global_trending(
    include_reddit=True,
    include_twitter=True,
    include_youtube=True,
    include_instagram=True,
    posts_per_source=50
)
```

### 7. **AI-Powered Discussion Summary** 🤖
**Location**: `summarizer.py`

**Features**:
- Automated theme extraction
- Sentiment distribution analysis
- Discussion snapshot generation
- Topic clustering and summarization

### 8. **Robust Time Analysis** 📊
**Location**: `time_analysis.py`

**Capabilities**:
- Flexible timestamp parsing
- Multiple time grouping options (hour/minute)
- Peak activity detection
- Trend growth rate calculation
- Keyword frequency over time

## 🎨 Visualization Features

### Interactive Charts
- **Plotly Integration**: Hover tooltips, zoom, pan
- **Peak Highlighting**: Visual emphasis on peak values
- **Responsive Design**: Adapts to different screen sizes
- **Export Options**: Built-in chart export capabilities

### Dashboard Layout
- **Tabbed Interface**: Organized analysis sections
- **Expandable Sections**: Detailed views on demand
- **Metric Cards**: Key insights at a glance
- **Status Indicators**: Real-time feedback

## 🔧 Technical Architecture

### Data Pipeline
1. **Source Selection** → Data fetching/adapters
2. **Preprocessing** → Text cleaning, tokenization
3. **Analysis** → Sentiment, topics, trends
4. **Visualization** → Interactive charts and metrics

### Error Handling
- **Graceful Degradation**: Fallback to sample data
- **API Resilience**: Retry logic and timeout handling
- **Data Validation**: Schema checking and type conversion
- **User Feedback**: Clear error messages and warnings

### Performance Optimizations
- **Caching**: Streamlit cache for expensive operations
- **Lazy Loading**: On-demand feature activation
- **Memory Management**: Efficient data structures
- **Async Operations**: Non-blocking data fetching

## 🚀 Advanced Usage Patterns

### Real-Time Monitoring
```python
# Enable Live Mode for continuous monitoring
# Set refresh interval based on use case
# Monitor trend velocity for early signals
```

### Comparative Analysis
```python
# Use VADER vs TextBlob comparison
# Compare activity patterns across topics
# Analyze cross-platform sentiment differences
```

### Custom Data Integration
```python
# Upload CSV with custom schema
# Automatic column detection
# Unified processing pipeline
```

## 📈 Analytics Capabilities

### Sentiment Analysis
- **VADER**: Rule-based, fast, social media optimized
- **TextBlob**: ML-based, more nuanced but slower
- **Comparison Mode**: Side-by-side analysis
- **Distribution Charts**: Visual sentiment breakdown

### Topic Modeling
- **LDA**: Latent Dirichlet Allocation
- **Coherence Scoring**: Topic quality metrics
- **Interactive Exploration**: Topic-by-topic analysis
- **Sentiment per Topic**: Combined analysis

### Trend Detection
- **Keyword Frequency**: Raw counts and rankings
- **TF-IDF**: Term importance scoring
- **Velocity Analysis**: Growth rate tracking
- **Temporal Patterns**: Time-based insights

## 🔐 Security & Privacy

### API Key Management
- **Environment Variables**: Secure credential storage
- **Optional Dependencies**: Graceful degradation without APIs
- **Rate Limiting**: Built-in delays and quotas
- **Error Masking**: No sensitive data in error messages

### Data Handling
- **No Data Persistence**: Unless explicitly collected
- **Local Processing**: All analysis happens client-side
- **Export Controls**: User-controlled data export
- **Privacy Compliance**: No tracking or data sharing

## 🎯 Use Cases

### Social Media Monitoring
- Brand sentiment tracking
- Crisis detection and response
- Influencer analysis
- Campaign performance monitoring

### Market Research
- Consumer trend identification
- Competitive analysis
- Product feedback analysis
- Industry sentiment tracking

### Academic Research
- Social discourse analysis
- Temporal trend studies
- Cross-platform comparison
- Sentiment pattern research

### Content Strategy
- Topic performance analysis
- Optimal posting time identification
- Content theme optimization
- Audience engagement insights

---

*This documentation reflects the enhanced feature set as of March 2026. Features are continuously evolving with user feedback and technological advancements.*
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
