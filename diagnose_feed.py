import requests
import time
import json

def diagnose():
    print("Diagnosing Moltbook API...")
    
    # Headers to mimic a real browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.moltbook.com/",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache"
    }
    
    # Try multiple variants
    urls = [
        "https://www.moltbook.com/api/v1/posts",
        "https://www.moltbook.com/api/v1/posts?sort=new",
        "https://www.moltbook.com/api/v1/posts?filter=new",
        f"https://www.moltbook.com/api/v1/posts?_t={int(time.time())}" # Bust cache
    ]
    
    target_titles = ["One more REDX check-in", "The Quiet Rules", "AzClaw Heartbeat"]
    
    for url in urls:
        print(f"\nTesting: {url}")
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code != 200:
                print(f"  Status: {resp.status_code}")
                continue
                
            data = resp.json()
            posts = data.get('posts', [])
            
            if not posts:
                print("  No posts found.")
                continue
                
            print(f"  Found {len(posts)} posts.")
            print(f"  Top 3 Titles:")
            for i, p in enumerate(posts[:3]):
                print(f"    {i+1}. [{p.get('created_at')}] {p.get('title')}")
                
            # Check for targets
            found = False
            for p in posts:
                if any(t in p.get('title', '') for t in target_titles):
                    print(f"  ✅ FOUND TARGET: {p.get('title')}")
                    found = True
            
            if not found:
                print("  ❌ Target posts NOT found in this response.")
                
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    diagnose()