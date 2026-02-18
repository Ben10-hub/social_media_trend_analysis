# Hybrid Social Media Trend & Sentiment Analysis (Streamlit + NLP)

This project is a simple **academic ML/NLP dashboard** that:
- Detects **trending topics** (hashtags, keyword frequency, TF‑IDF, LDA topics)
- Computes **sentiment** (Positive / Neutral / Negative) using **VADER**
- Visualizes results in an interactive **Streamlit** app

## Files
- `app.py`: Streamlit application
- `data/sample_social_posts.csv`: demo dataset (has a `text` column)
- `requirements.txt`: Python dependencies

## Dataset format
Upload a CSV with at least:
- `text`: social media post text

Extra columns are allowed (they’ll be ignored by the app).

## Run locally
Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Start the app:

```bash
streamlit run app.py
```

Notes:
- On first run, NLTK may download required resources automatically (tokenizers, stopwords, VADER lexicon).
- For better LDA topics, use a larger dataset (roughly **200+ posts** is ideal).

## Using the sample dataset
In the sidebar, enable **Use sample dataset** (or upload your own CSV).

## What you’ll see in the dashboard
- Top trending keywords (frequency)
- Top hashtags (frequency)
- Top TF‑IDF terms
- LDA discovered topics + topic sentiment
- Overall sentiment distribution
- Word cloud
- Downloadable CSV of sentiment results

