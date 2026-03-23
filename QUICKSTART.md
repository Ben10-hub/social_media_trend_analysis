# 🚀 Quick Start Guide (Updated)

## What's New (March 2026 refactor)
- Sidebar data sources now:
  - `Sample`
  - `Upload CSV`
  - `Quick Reddit`
  - `Quick X`
  - `Quick YouTube`
  - `Quick Instagram`
  - `Hacker News`
  - `News RSS`
  - `Load from collected`
- Removed API options that used to require custom keys for the main flow.
- Added consolidated tabs:
  - `📊 Overview`
  - `📈 Trends`
  - `🧠 Topics (LDA)`
  - `⏱ Time Trends`
  - `🌍 Geographic`
  - `🔍 Search`
- New advanced insights:
  - Trend Velocity chart
  - Topic coherence (c_v)
  - VADER vs TextBlob comparison panel
  - AI summary built into Trends tab

## Quick start
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Recommended package for hot reload
```bash
pip install watchdog
```

## Quick path
1. Start app and pick a source
2. Confirm loaded dataframe
3. Explore tabs:
   - Overview: metrics, sentiment, wordcloud, trend sentiment
   - Trends: top keywords/hashtags/TF-IDF + velocity + AI summary
   - Topics: LDA + coherence + topic sentiment
   - Time Trends: post volume and growth
   - Geographic: map + top country chart
   - Search: boolean query analyzer

## Notes
- textblob required for model comparison: `pip install textblob`
- feedparser required for Quick X / RSS (already in requirements)
- no API keys needed for Hacker News / News RSS

### 3️⃣ Advanced Search with Boolean Operators
New tab: **🔍 Subquery Search**

**Syntax examples:**
```
AI -hype              → Find AI posts but exclude hype
trending |viral       → Trending posts, boost if viral
technology -basics    → Advanced tech topics only
```

### 4️⃣ Geographic Insights Enhanced
New tab: **Geographic Insights** (improved!)

**What's new:**
- See world map of where posts originate
- See top countries posting about your topic
- Automatic country detection

**To see it:**
1. Load sample data with location: Use built-in sample
2. Or upload CSV with "location" column

---

## 📍 Step-by-Step Usage

### Try YouTube Scraping
1. Open `app.py` in Streamlit
2. In sidebar → Select "Quick YouTube (No API)"
3. Change query to any topic (e.g., "AI trends", "gaming")
4. Adjust "Videos to fetch" (5-50)
5. Click "Run" → See YouTube trending data analyzed

### Try Global Trending
1. In sidebar → Select "Global Trending"
2. Wait for data collection from all 4 platforms
3. See sidebar notification: "✅ Collected X posts from Y platforms"
4. Analyze combined data across all tabs

### Try Subquery Search
1. Go to **🔍 Subquery Search** tab
2. Type search: `machine learning -basics`
3. Optionally filter by platform (Reddit, Twitter, etc.)
4. See results with:
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
