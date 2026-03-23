# 🚀 Startup Guide (Updated)

## ✅ Your Setup is Complete!

Your app is now aligned with the new tab structure and data source logic.

- `textblob` installed for VADER vs TextBlob comparison.
- `watchdog` recommended for Streamlit file watch performance.
- No API key needed for Hacker News and News RSS.
- Legacy source set now: Sample, Upload CSV, Quick Reddit, Quick X, Quick YouTube, Quick Instagram, Hacker News, News RSS, Load from collected.

## How to run
```bash
cd "/Users/jaswanth/Desktop/proj_2 copy 4"
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Fatal shortcuts and updates
- Removed: `Fetch Reddit/Twitter/YouTube/Instagram`, `Global Trending` as top-level data sources.
- Added: free data sources (Hacker News + News RSS) and expanded Overview/Trends/Topics outputs.
- Keep: `Collect Now` and collected data loading (via adapter) for historical data.

---

## 🎯 How to Run the Project

### Option 1: Quick Start (Recommended) 🎯
```bash
cd "/Users/jaswanth/Desktop/proj_2 copy 3"
bash run.sh
```

This will:
1. ✅ Create/activate virtual environment
2. ✅ Install all dependencies
3. ✅ Install YouTube API client
4. ✅ Verify .env configuration
5. ✅ Launch Streamlit app

---

### Option 2: Manual Steps 
```bash
# Navigate to project
cd "/Users/jaswanth/Desktop/proj_2 copy 3"

# Activate virtual environment
source .venv/bin/activate

# Install remaining packages (if needed)
pip install google-api-python-client

# Run the app
streamlit run app.py
```

---

## 📺  Now You Can Use:

### New YouTube Features Available:

#### 1. **Fetch YouTube (with API)** ← NOW ACTIVE! 
- Shows trending YouTube videos
- By region/country
- High quality results
- Real descriptions and metadata

#### 2. **Quick YouTube (No API)**
- Backup option: search via RSS
- Works without API key
- Good for quick searches

#### 3. **Global Trending**
- Combines YouTube + Reddit + Twitter + Instagram
- YouTube data now included!

---

## 🧪 Test YouTube API

Once the app is running, test like this:

1. **In Streamlit Sidebar:**
   - Select: `Fetch YouTube` (the API version)
   - Or select: `Quick YouTube (No API)`

2. **See YouTube Results:**
   - Real trending videos
   - High-quality metadata
   - Dates and descriptions

3. **Analyze Like Any Other Data:**
   - View keywords
   - Sentiment analysis
   - Geographic insights
   - Search with boolean operators

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