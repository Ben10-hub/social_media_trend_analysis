#!/usr/bin/env bash
# Quick Start Script for Trending Topics Analyzer

echo "🚀 Starting Trend & Sentiment Analyzer with YouTube API..."
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "✅ Activating virtual environment..."
source .venv/bin/activate

# Check if requirements are installed
echo "📦 Checking dependencies..."
pip install -q streamlit pandas nltk gensim scikit-learn wordcloud plotly pycountry feedparser requests tweepy python-dotenv > /dev/null 2>&1

# Install YouTube API
echo "📦 Installing Google YouTube API client..."
pip install -q google-api-python-client > /dev/null 2>&1

# Check .env file
if [ -f ".env" ]; then
    echo "✅ .env file found with YouTube API key configured"
else
    echo "⚠️  No .env file found"
fi

echo ""
echo "=========================================="
echo "🎉 Setup Complete!"
echo "=========================================="
echo ""
echo "Your YouTube API is ready to use!"
echo ""
echo "Starting Streamlit app..."
echo ""

# Run the app
streamlit run app.py
