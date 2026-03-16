def fetch_real_reddit_data():
    api_key = os.getenv('RAPIDAPI_KEY')
    host = "reddit3.p.rapidapi.com" 
    url = f"https://{host}/v1/reddit/search"
    
    # Simpler query for testing
    params = {
        "search": "news",
        "filter": "posts",
        "sortType": "relevance"
    }

    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": host
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        
        # Check if 'results' exists, if not, print keys so we can find where data is
        posts = data.get('results', [])
        
        if not posts:
            print(f"⚠️ No results in 'results' key. Available keys are: {list(data.keys())}")
            # Some versions use 'data' or 'posts'
            posts = data.get('data', []) or data.get('posts', [])

        if posts:
            print(f"✅ SUCCESS! Found {len(posts)} posts.")
            print(f"First Title: {posts[0].get('title', 'No Title Found')}")
        else:
            print("❌ Still found 0 posts. Try changing the 'search' word to something else.")

    except Exception as e:
        print(f"⚠️ Connection error: {e}")