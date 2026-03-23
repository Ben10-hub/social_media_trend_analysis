# 🚀 Quick Start Guide - Enhanced Dashboard

## Welcome to the Advanced Social Media Analytics Platform!

This guide will get you up and running with the latest features including **Trend Velocity**, **Activity Insights**, and **Live Mode**.

## ⚡ Quick Setup (3 minutes)

```bash
# 1. Clone and navigate
git clone https://github.com/Ben10-hub/social_media_trend_analysis.git
cd social_media_trend_analysis

# 2. Setup environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch app
streamlit run app.py
```

## 🎯 First Steps

### 1. Choose Your Data Source
The sidebar offers multiple options:
- **Sample**: Test with built-in dataset (recommended for first run)
- **Quick Reddit/X/YouTube/Instagram**: No-API scraping
- **Hacker News**: Tech stories from HN
- **News RSS**: Tech news from major sources
- **Upload CSV**: Import your own data

### 2. Explore the Dashboard
Six main tabs provide comprehensive analysis:

#### 📊 Overview Tab
- **Dataset metrics**: Post count, platform distribution
- **Sentiment analysis**: VADER sentiment with pie charts
- **Word clouds**: Visual keyword representation
- **Trend sentiment**: Sentiment over time

#### 📈 Trends Tab
- **Top keywords**: Most frequent terms
- **Hashtags**: Popular hashtag analysis
- **TF-IDF**: Important term scoring
- **Trend Velocity**: Growth rate visualization ⭐ **NEW**
- **AI Summary**: Automated discussion themes ⭐ **NEW**

#### 🧠 Topics Tab
- **LDA Topics**: Topic modeling with coherence scores
- **Topic visualization**: Interactive topic exploration
- **Sentiment per topic**: Combined analysis

#### ⏱️ Time Trends Tab
- **Post volume**: Activity over time
- **Activity Insights**: Hourly patterns with bar/heatmap ⭐ **NEW**
- **Peak detection**: When discussions are most active

#### 🌍 Geographic Tab
- **World map**: Location-based visualization
- **Country rankings**: Top posting countries
- **Location insights**: Geographic trends

#### 🔍 Search Tab
- **Boolean queries**: Advanced search syntax
- **Platform filtering**: Search specific sources
- **Result analysis**: Detailed search results

## 🆕 New Features to Try

### 1. **Trend Velocity Analysis** 📈
**Location**: Trends tab → Trend Velocity expander

**What to do**:
1. Load time-series data (Sample or collected data works)
2. Go to Trends tab
3. Expand "Trend Velocity" section
4. See smoothed growth rates for top keywords
5. Note the clean visualization showing rising/falling trends

### 2. **Activity Insights** ⏰
**Location**: Time Trends tab → Activity Insights expander

**What to do**:
1. Load data with timestamps
2. Go to Time Trends tab
3. Expand "Activity Insights"
4. Select a keyword from the dropdown
5. Toggle between Bar Chart and Heatmap views
6. Check the insight cards for peak activity metrics

### 3. **Live Mode** 🔄
**Location**: Sidebar → Real-time collection section

**What to do**:
1. Select a data source (e.g., Quick Reddit)
2. In sidebar, check "Enable Live Mode"
3. Adjust refresh interval (10-120 seconds)
4. Notice the status indicator at top changes to "Live Mode Active"
5. Watch data auto-refresh and update automatically

## 🎨 Advanced Usage Examples

### Real-Time Monitoring Setup
```bash
# 1. Select Quick Reddit source
# 2. Enable Live Mode with 30s refresh
# 3. Monitor Trend Velocity for emerging topics
# 4. Use Activity Insights to find optimal posting times
```

### Comparative Analysis
```bash
# 1. Load data from different sources
# 2. Compare sentiment distributions
# 3. Analyze topic coherence across platforms
# 4. Use geographic insights for location-based trends
```

### Custom Data Analysis
```bash
# 1. Upload CSV with text and timestamp columns
# 2. Run preprocessing and analysis
# 3. Explore all tabs for comprehensive insights
# 4. Export results for further analysis
```

## 🔧 Configuration Options

### Sidebar Controls
- **Number of trends**: Adjust analysis depth (5-50)
- **LDA topics**: Topic modeling complexity (2-12)
- **LDA passes**: Model training iterations (5-30)
- **Time grouping**: Hour or minute resolution

### Data Source Settings
- **Quick Reddit**: Subreddit selection + post limit
- **Quick X**: Search query + Nitter instance
- **Quick YouTube**: Search terms + video limit
- **Quick Instagram**: Hashtag + post limit

## 🆘 Troubleshooting

### Common Issues & Solutions

**App won't start**:
- Check Python version (3.8+ recommended)
- Ensure all dependencies installed: `pip install -r requirements.txt`
- Try running in clean virtual environment

**No data loading**:
- Start with "Sample" data source for testing
- Check internet connection for scraping sources
- Verify CSV format for uploads

**Charts not displaying**:
- Ensure matplotlib backend is configured
- Check for missing optional dependencies
- Try refreshing the page

**Live Mode not working**:
- Check browser console for errors
- Ensure stable internet connection
- Try shorter refresh intervals

**API errors**:
- Most features work without API keys
- Check `.env` file format for optional APIs
- Fall back to "Quick" (no-API) versions

### Performance Tips
- Use smaller datasets for faster analysis
- Disable Live Mode when not needed
- Close unused browser tabs
- Use sample data for feature testing

## 📚 Learning Resources

### Feature Documentation
- **[Features Guide](FEATURES.md)**: Detailed feature explanations
- **[README](README.md)**: Project overview and setup
- **[Startup Guide](STARTUP.md)**: Configuration and deployment

### API Setup (Optional)
- **Reddit**: Create app at reddit.com/prefs/apps
- **YouTube**: Google Cloud Console API key
- **Instagram**: Meta Graph API token
- **X/Twitter**: Twitter Developer Portal

## 🎯 Next Steps

### Beginner Path
1. ✅ Complete basic setup
2. ✅ Explore all tabs with sample data
3. ✅ Try different data sources
4. 🔄 Enable Live Mode for real-time monitoring

### Advanced Path
1. ✅ Setup API credentials for enhanced features
2. ✅ Upload custom datasets
3. ✅ Use boolean search for complex queries
4. 🔄 Integrate with `collect_real_time.py` for continuous data

### Development Path
1. ✅ Review source code structure
2. ✅ Understand adapter pattern
3. ✅ Modify existing features
4. 🔄 Add new data sources or analysis methods

## 💡 Pro Tips

- **Start small**: Use sample data to learn features
- **Live Mode**: Great for monitoring, but can be resource-intensive
- **Boolean search**: Powerful for filtering specific content
- **Trend Velocity**: Best with time-series data from multiple sources
- **Activity Insights**: Most useful for understanding audience behavior

## 🆘 Getting Help

- **Documentation**: Check FEATURES.md for detailed explanations
- **GitHub Issues**: Report bugs or request features
- **Community**: Join discussions for tips and tricks

---

**Happy analyzing! 🎉**

*Last updated: March 2026*
   - Platform breakdown chart
   - Sentiment analysis
   - Top keywords found
   - Download results as CSV

### Try Geographic Insights
1. Load sample data (uses built-in sample with locations)
2. Go to **Geographic Insights** tab
3. See:
   - World map colored by post count
   - Top 10 countries bar chart
   - Country distribution

---

## 🔧 Configuration (Optional APIs)

### YouTube API (Optional)
Get API key: https://console.cloud.google.com
```env
YOUTUBE_API_KEY=your_key_here
```

### Instagram API (Optional)
Get token: https://developers.facebook.com/apps/
```env
INSTAGRAM_ACCESS_TOKEN=your_token_here
```

### Already Supported
- Reddit, Twitter/X, and no-API options work immediately
- No configuration needed for "Quick" versions

---

## 📊 Sample Workflows

### Workflow 1: Analyze Global Trends
```
1. Sidebar: Select "Global Trending"
2. Wait for collection (2-3 minutes)
3. Overview tab: See sentiment distribution
4. Trends tab: View top keywords from all platforms
5. Subquery Search: Deep-dive into specific topics
6. Geographic Insights: See where people discuss it
```

### Workflow 2: Deep Search
```
1. Sidebar: Select "Quick Reddit (No API)" or "Quick YouTube (No API)"
2. Enter specific topic
3. Subquery Search tab: Use boolean operators
4. Example: "climate -denialism -skeptic"
5. Export results as CSV
```

### Workflow 3: Geographic Analysis
```
1. Sidebar: Select any source that supports location
2. Twitter → Geographic Insights (shows by user location)
3. View choropleth map
4. See which countries are discussing what topics
```

---

## 📁 New Files Created

| File | Purpose |
|------|---------|
| `adapters/youtube_adapter.py` | YouTube scraping & API integration |
| `adapters/instagram_adapter.py` | Instagram scraping & API integration |
| `global_trends.py` | Collect from all platforms simultaneously |
| `subquery_search.py` | Boolean search & advanced filtering |
| `data/sample_social_posts_with_location.csv` | Sample with geographic data |
| `FEATURES.md` | Full feature documentation |

---

## 🎯 Key Features by Tab

### 🔍 Subquery Search (NEW!)
```python
Search: "AI -hype"
Results:
├── Matches: 342
├── Platform breakdown
├── Sentiment analysis
└── Top keywords
```

### 🗺️ Geographic Insights (Enhanced!)
```
World Map View:
├── Choropleth (countries colored by count)
├── Top 10 countries bar chart
└── Export option
```

### 📈 New Sidebar Options
```
Data source:
├── Global Trending ← NEW
├── Fetch YouTube ← NEW
├── Fetch Instagram ← NEW
├── Quick YouTube (No API) ← NEW
├── Quick Instagram (No API) ← NEW
└── [existing sources...]
```

---

## ⚡ Performance Tips

1. **Global Trending** takes 2-3 minutes (collects from 4 sources)
2. **Quick sources** (no API) are faster but less data
3. **API sources** are slowest but most comprehensive
4. Use **Platform filter** in Subquery Search to narrow results

---

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| "feedparser not installed" | `pip install feedparser` |
| YouTube/Instagram returns nothing | Try "Quick" version or check API key |
| No Location data | Load sample or add location column to CSV |
| Search returns 0 results | Try simpler query, remove `-` filters |
| Global Trending takes too long | Check internet, some platforms may be slow |

---

## 📚 Examples by Use Case

### Monitor AI Industry Trends
```
1. Global Trending (all platforms)
2. Subquery: "AI -hype |innovation"
3. Sentiment: See positive/negative ratio
4. Time-based: Track growth
5. Geography: Which countries lead in AI discussion
```

### Find Specific Topic Discussions
```
1. Load platform (Reddit/Twitter/YouTube)
2. Subquery: "topic -spam -bot"
3. Top keywords: See related discussions
4. Export: Save for further analysis
```

### Analyze Emerging Topics
```
1. Global Trending (captures across platforms)
2. Platform Comparison: Reddit vs Twitter vs YouTube
3. Time-based: See if it's growing
4. LDA Topics: Auto-discover related topics
```

---

## 🎓 Learning Path

1. ✅ Start with **Sample** data (familiarize yourself)
2. ✅ Try **Quick Reddit** or **Quick X** (single platform)
3. ✅ Explore **Global Trending** (multi-platform)
4. ✅ Try **Subquery Search** (boolean operators)
5. ✅ Analyze **Geographic Insights** (location data)
6. ✅ Create custom **CSV** with your data
7. ✅ Configure **API keys** for larger datasets

---

## 💡 Pro Tips

- Use `-` filters liberally to exclude noise: `trending -fake -spam`
- Use `|` to find related concepts: `AI |ML |DeepLearning`
- Global Trending best for discovering new topics
- YouTube has most visuals, Reddit has most discussion
- Export CSV results for external analysis

---

**Enjoy exploring real-time trends! 🚀**
