import requests
import time
from datetime import datetime, timezone

def verify_latest_news():
    print("Verifying fix for 'New' news...")
    
    # Wait for the scraper to run at least once with the new URL
    print("Skipping wait (assuming scraper is running)...")
    # time.sleep(20)
    
    try:
        # Fetch from our local API with sort=new
        url = "http://localhost:8000/api/posts?sort=new&limit=5"
        resp = requests.get(url)
        posts = resp.json()
        
        if not posts:
            print("❌ No posts returned from API.")
            return

        print(f"Top 5 'New' posts in DB:")
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        found_today = False
        
        for p in posts:
            created_at = p['created_at']
            title = p['title']
            print(f"  [{created_at}] {title[:40]}...")
            
            # Check if date is today (2026-02-24)
            if created_at.startswith(today_str):
                found_today = True
        
        if found_today:
            print("\n✅ SUCCESS: Found posts from today! The 'New' feed is working.")
        else:
            print(f"\n❌ FAILURE: No posts from today ({today_str}) found. Still showing old data?")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    verify_latest_news()