import requests
import time
import json

def check():
    try:
        url = "http://localhost:8000/api/posts?sort=new&limit=5"
        print(f"Checking {url}...")
        resp = requests.get(url)
        data = resp.json()
        print(f"Total posts returned: {len(data)}")
        if data:
            print("First Post Title:", data[0].get('title'))
            print("First Post Title (ZH):", data[0].get('title_zh'))
            print("First Post Author:", data[0].get('author', {}).get('name'))
            print("First Post Created At:", data[0].get('created_at'))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check()