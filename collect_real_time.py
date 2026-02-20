"""
Standalone script for scheduled real-time collection.
Run in a separate terminal:
  python collect_real_time.py
Fetches from Reddit every 5 minutes and appends to data/social_data.db.
Set REDDIT_* in .env before running.
"""
import os
import sys
import time
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from adapters.reddit_adapter import fetch_reddit_posts
from data_store import append_posts, get_db_path


def main():
    interval_min = int(os.getenv("COLLECT_INTERVAL_MIN", "5"))
    subreddits = os.getenv("REDDIT_SUBREDDITS", "python,technology,worldnews").split(",")

    print(f"Starting collection every {interval_min} min. Data: {get_db_path()}")
    print("Ctrl+C to stop.")

    while True:
        try:
            df, err = fetch_reddit_posts(subreddits=subreddits, limit_per_sub=25)
            if err:
                print(f"[{time.strftime('%H:%M:%S')}] {err}")
            elif df is not None and not df.empty:
                added, append_err = append_posts(df, dedup=True)
                if append_err:
                    print(f"[{time.strftime('%H:%M:%S')}] Append error: {append_err}")
                else:
                    print(f"[{time.strftime('%H:%M:%S')}] Added {added} new posts. Total run continuing.")
        except KeyboardInterrupt:
            print("\nStopped.")
            break
        except Exception as e:
            print(f"[{time.strftime('%H:%M:%S')}] Error: {e}")

        time.sleep(interval_min * 60)


if __name__ == "__main__":
    main()
