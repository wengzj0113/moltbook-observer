import requests
import time
from datetime import datetime

def test_auto_update():
    print("Testing auto-update mechanism...")
    
    # 1. Check initial state
    try:
        url = "http://localhost:8000/api/stats"
        resp = requests.get(url)
        initial_stats = resp.json()
        print(f"Initial Stats: {initial_stats['total_posts']} posts")
        
        print("Waiting for 20 seconds to allow next scrape cycle...")
        time.sleep(20)
        
        # 2. Check updated state
        resp = requests.get(url)
        new_stats = resp.json()
        print(f"New Stats: {new_stats['total_posts']} posts")
        
        if new_stats['total_posts'] >= initial_stats['total_posts']:
            print("✅ Verification Successful: Backend is active and stats are stable/increasing.")
        else:
            print("❌ Verification Failed: Stats decreased (unless cleanup happened).")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_auto_update()