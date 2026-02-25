import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_moltbook_api():
    # Try different sort parameters
    endpoints = [
        "https://www.moltbook.com/api/v1/posts",
        "https://www.moltbook.com/api/v1/posts?sort=new",
        "https://www.moltbook.com/api/v1/posts?sort=latest",
        "https://www.moltbook.com/api/v1/posts?order=desc",
        "https://www.moltbook.com/api/v1/posts?filter=new"
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
    }
    
    for url in endpoints:
        try:
            logger.info(f"Testing {url}...")
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                posts = data.get("posts", [])
                if posts:
                    first_post = posts[0]
                    print(f"  First Post: {first_post.get('created_at')} - {first_post.get('title')[:30]}")
                else:
                    print("  No posts found.")
            else:
                print(f"  Status: {response.status_code}")
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    test_moltbook_api()