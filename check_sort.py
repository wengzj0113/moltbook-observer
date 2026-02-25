import requests
import json

def check_sort():
    try:
        url = "http://localhost:8000/api/posts?sort=new&limit=5"
        print(f"Checking {url}...")
        resp = requests.get(url)
        data = resp.json()
        
        print(f"Returned {len(data)} posts.")
        for i, p in enumerate(data):
            print(f"{i+1}. {p['created_at']} - {p['title'][:30]}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_sort()