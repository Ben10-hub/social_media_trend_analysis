# 🚀 Startup Guide - Complete Setup & Configuration

## Welcome! 🎉

Your enhanced social media analytics dashboard is ready with the latest features including **Trend Velocity**, **Activity Insights**, and **Live Mode**. This guide will help you get everything running smoothly.

## ⚡ Quick Launch (Recommended)

### Option 1: Automated Setup
```bash
# Run the setup script (if available)
chmod +x run.sh
./run.sh
```

### Option 2: Manual Setup
```bash
# Navigate to project directory
cd "/Users/jaswanth/Desktop/proj_2 copy 4"

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt

# Optional: Install performance enhancer
pip install watchdog

# Launch the application
streamlit run app.py
```

## ✅ Verification Checklist

After starting the app, verify these work:

- [ ] **Sample Data**: Loads without errors
- [ ] **Quick Sources**: Reddit, X, YouTube, Instagram work
- [ ] **News Sources**: Hacker News and RSS feeds load
- [ ] **Trend Velocity**: Shows in Trends tab
- [ ] **Activity Insights**: Available in Time Trends tab
- [ ] **Live Mode**: Toggle works in sidebar

## 🎯 Feature Overview

### Core Functionality
- **📊 Overview**: Dataset metrics, sentiment analysis, word clouds
- **📈 Trends**: Keywords, hashtags, TF-IDF, trend velocity
- **🧠 Topics**: LDA topic modeling with coherence scores
- **⏱️ Time Trends**: Activity insights with interactive charts
- **🌍 Geographic**: Location-based analysis and mapping
- **🔍 Search**: Boolean query search with advanced filters

### New Features (March 2026)
- **Trend Velocity**: True growth rate visualization
- **Activity Insights**: Hourly posting pattern analysis
- **Live Mode**: Auto-refresh with configurable intervals
- **Enhanced Adapters**: Improved YouTube and Instagram support

## 🔧 Configuration Options

### Environment Variables (.env file)
Create a `.env` file in the project root for optional API access:

```bash
# Reddit API (optional)
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=TrendSentimentApp/1.0

# YouTube API (optional)
YOUTUBE_API_KEY=your_api_key

# Instagram API (optional)
INSTAGRAM_ACCESS_TOKEN=your_access_token

# X/Twitter API (optional)
TWITTER_BEARER_TOKEN=your_bearer_token

# Collection settings
COLLECT_INTERVAL_MIN=5
```

### Sidebar Controls
- **Number of trends**: Analysis depth (5-50, default: 15)
- **LDA topics**: Topic count (2-12, default: 5)
- **LDA passes**: Training iterations (5-30, default: 10)
- **Time grouping**: Resolution (hour/minute, default: hour)

## 📊 Data Sources Guide

### 1. Sample Dataset
- **Best for**: First-time users, feature testing
- **Content**: Pre-loaded social media posts
- **Features**: All analytics work out-of-the-box

### 2. Quick Scrapers (No API Required)
- **Quick Reddit**: Subreddit posts via RSS/JSON
- **Quick X**: Twitter search via Nitter RSS
- **Quick YouTube**: Video search via HTML parsing
- **Quick Instagram**: Hashtag posts via web scraping

### 3. News Sources
- **Hacker News**: Tech stories from HN front page
- **News RSS**: Tech news from RSS feeds (BBC, TechCrunch, etc.)

### 4. Advanced Options
- **Upload CSV**: Import custom datasets
- **Load from collected**: Use SQLite database
- **Real-time collection**: Manual/API-based fetching

## 🆕 Testing New Features

### Trend Velocity Analysis
1. Load time-series data (Sample or collected)
2. Navigate to **Trends** tab
3. Expand **"Trend Velocity"** section
4. Observe smoothed growth rate curves
5. Note top 3-5 keywords with rising/falling patterns

### Activity Insights
1. Load data with timestamps
2. Go to **Time Trends** tab
3. Expand **"Activity Insights"**
4. Select keyword from dropdown
5. Toggle between Bar Chart and Heatmap
6. Review peak hour metrics

### Live Mode
1. Select any data source
2. Enable **"Live Mode"** in sidebar
3. Set refresh interval (10-120 seconds)
4. Observe auto-refresh and status indicator
5. Data updates automatically from selected source

## 🔧 Troubleshooting

### Common Issues

**"Module not found" errors**:
```bash
# Ensure all dependencies installed
pip install -r requirements.txt

# Check Python version (3.8+ recommended)
python --version
```

**App won't start**:
```bash
# Try clean environment
deactivate
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

**Charts not rendering**:
- Check matplotlib configuration
- Ensure plotly is installed
- Try different browser

**API failures**:
- Most features work without APIs
- Check `.env` file syntax
- Use "Quick" versions as fallback

**Live Mode issues**:
- Check browser console for errors
- Ensure stable internet connection
- Try shorter refresh intervals

### Performance Optimization
```bash
# Install watchdog for better file watching
pip install watchdog

# Use smaller datasets for faster analysis
# Disable Live Mode when not monitoring
# Close unused browser tabs
```

## 📚 API Setup (Optional but Recommended)

### Reddit API Setup
1. Visit [Reddit Apps](https://www.reddit.com/prefs/apps)
2. Create new app (type: script)
3. Copy client ID and secret
4. Add to `.env` file

### YouTube API Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project and enable YouTube Data API v3
3. Create API key
4. Add `YOUTUBE_API_KEY=your_key` to `.env`

### Instagram API Setup
1. Visit [Meta Developers](https://developers.facebook.com/)
2. Create app with Instagram Basic Display
3. Get access token
4. Add `INSTAGRAM_ACCESS_TOKEN=your_token` to `.env`

### X/Twitter API Setup
1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
2. Create project and app
3. Get Bearer token
4. Add `TWITTER_BEARER_TOKEN=your_token` to `.env`

## 🚀 Advanced Usage

### Real-Time Monitoring
```bash
# Enable Live Mode for continuous monitoring
# Use Trend Velocity for early trend detection
# Monitor Activity Insights for optimal posting times
```

### Background Collection
```bash
# Run continuous collection in separate terminal
python collect_real_time.py

# Data stored in data/social_data.db
# Use "Load from collected" source to analyze
```

### Custom Data Integration
- Upload CSV with columns: `text`, `timestamp`, `platform`
- Automatic column detection and processing
- Full analytics pipeline support

## 📁 Project Structure

```
├── app.py                    # Main Streamlit application
├── adapters/                 # Data source adapters
│   ├── youtube_adapter.py    # YouTube scraping & API
│   ├── instagram_adapter.py  # Instagram scraping & API
│   └── ...
├── data/                     # Sample datasets
├── data_store.py            # SQLite operations
├── time_analysis.py         # Time-based analytics
├── summarizer.py           # AI discussion summary
├── subquery_search.py      # Boolean search engine
├── global_trends.py        # Multi-platform aggregation
├── collect_real_time.py    # Background collection
├── requirements.txt         # Dependencies
└── docs/                    # Documentation
```

## 🎯 Success Metrics

After setup, you should be able to:

- [ ] Load sample data without errors
- [ ] Switch between all data sources
- [ ] Generate sentiment analysis
- [ ] View trend velocity charts
- [ ] Use activity insights
- [ ] Enable live mode successfully
- [ ] Perform boolean searches
- [ ] Export analysis results

## 💡 Pro Tips

- **Start with Sample**: Perfect for learning all features
- **Live Mode**: Excellent for monitoring, but resource-intensive
- **API Keys**: Optional but enhance data quality
- **Boolean Search**: Powerful for precise content filtering
- **Trend Velocity**: Best with diverse time-series data

## 🆘 Support Resources

- **[README](README.md)**: Project overview
- **[Features](FEATURES.md)**: Detailed feature documentation
- **[Quick Start](QUICKSTART.md)**: Step-by-step usage guide
- **GitHub Issues**: Bug reports and feature requests

## 🎉 You're All Set!

Your advanced social media analytics platform is now ready. Explore the features, try different data sources, and enjoy discovering insights from social media data!

---

*Dashboard Version: Enhanced 2026 | Last Updated: March 2026*

---

## 🌍 YouTube API Features

| Feature | Status | Description |
|---------|--------|-------------|
| Trending Videos | ✅ Active | By region (US, UK, etc.) |
| Video Search | ✅ Available | Search any topic |
| Regional Trending | ✅ Supported | Different countries |
| Metadata | ✅ Enhanced | Title, description, published date |
| API Rate Limits | ✅ Included | 10,000 queries/day per API key |

---

## 💻 What to Expect

### Sidebar Data Sources (Updated):
```
✅ Sample
✅ Upload CSV
✅ Load from collected
✅ Global Trending          ← Includes YouTube!
✅ Fetch Reddit
✅ Fetch Twitter
✅ Fetch YouTube           ← NEW! Now working!
✅ Fetch Instagram
✅ Quick Reddit (No API)
✅ Quick X (No API)
✅ Quick YouTube (No API)  ← Still available as backup
✅ Quick Instagram (No API)
```

---

## 📊 Example Workflows with YouTube

### Workflow 1: Analyze YouTube Trends
```
1. Sidebar: Select "Fetch YouTube"
2. Wait for data collection
3. View "Overview" tab: Sentiment of YouTube videos
4. View "Trends" tab: Top keywords in YouTube titles
5. View "Geographic Insights": Where videos are popular
6. Use "Subquery Search": Find videos about specific topics
```

### Workflow 2: Global Trending (including YouTube)
```
1. Sidebar: Select "Global Trending"
2. System collects from Reddit + Twitter + YouTube + Instagram
3. See combined trends across all platforms
4. YouTube content mixed with social media
5. Advanced analytics on all combined data
```

### Workflow 3: Search YouTube Videos
```
1. Sidebar: Select "Quick YouTube (No API)"
2. Enter search term: "AI trends 2026"
3. Browse results in "Dataset Preview"
4. Analyze with all tools (sentiment, keywords, etc.)
```

---

## 🔍 Feature Highlights

### YouTube Trending by Region
- United States (US)
- United Kingdom (GB)
- Europe (DE, FR, etc.)
- Asia (IN, JP, CN, etc.)
- And 190+ countries!

### YouTube Metadata Extracted
- Video title
- Description
- Upload date
- View statistics
- Category

---

## 🎓 Learning Path

1. ✅ **Start Simple**: Select "Sample" data first
2. ✅ **Try YouTube**: Select "Fetch YouTube" 
3. ✅ **Run Analysis**: Explore all 10 tabs
4. ✅ **Search Videos**: Use Subquery Search tab
5. ✅ **Go Global**: Try "Global Trending" with YouTube included

---

## ⚙️ API Configuration

Your current setup:
```
✅ YouTube API Key: CONFIGURED
✅ RapidAPI Key: CONFIGURED
⚠️  Reddit API: Optional (still works with Quick Reddit)
⚠️  Twitter API: Optional (still works with Quick X)
⚠️  Instagram API: Optional (still works with Quick Instagram)
```

All optional APIs can be added to `.env` later if needed.

---

## 🚨 Troubleshooting

### YouTube Returns No Results
```
Solution 1: Check internet connection
Solution 2: Try different region code
Solution 3: Use "Quick YouTube (No API)" as backup
```

### App Won't Start
```bash
# Try these steps:
source .venv/bin/activate
pip install -r requirements.txt
pip install google-api-python-client
streamlit run app.py
```

### "API Key Invalid" Error
```
Check: .env file has correct API key
Check: No extra spaces in .env
Check: Run from project directory
```

---

## 📱 Mobile Access

After starting the app:
- **Desktop**: http://localhost:8501
- **Network**: Your machine IP:8501

---

## 🎉 You're All Set!

Everything is ready to go! 

**Just run:**
```bash
bash run.sh
```

Or:
```bash
streamlit run app.py
```

**Then enjoy exploring trends from YouTube + Reddit + Twitter + Instagram!** 🚀

---

## 📞 Quick Reference

| Task | Command |
|------|---------|
| Start app | `bash run.sh` |
| Start (manual) | `streamlit run app.py` |
| View .env | `cat .env` |
| Exit app | Press `Ctrl+C` |
| Refresh browser | `R` key in Streamlit |

---

**Happy trend hunting! 🎯**