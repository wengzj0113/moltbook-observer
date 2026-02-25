import requests
from bs4 import BeautifulSoup
import json
import os

def analyze():
    url = "https://www.moltbook.com"
    print(f"Fetching {url}...")
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        # Save HTML for inspection
        with open("d:\\openclaw\\moltbook-observer\\homepage.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        print("Saved homepage.html")

        # Probe candidates
        candidates = [
            "https://www.moltbook.com/api/v1/posts",
            "https://www.moltbook.com/api/v1/feed",
            "https://www.moltbook.com/api/posts",
            "https://www.moltbook.com/api/feed",
            "https://www.moltbook.com/feed.json",
            "https://www.moltbook.com/posts.json"
        ]
        
        for api_url in candidates:
            print(f"Probing API: {api_url}...")
            try:
                api_response = requests.get(api_url, timeout=5)
                print(f"  Status: {api_response.status_code}")
                if api_response.status_code == 200:
                    print("  SUCCESS!")
                    try:
                        data = api_response.json()
                        print(f"  Data type: {type(data)}")
                        # print(str(data)[:200])
                        with open(f"d:\\openclaw\\moltbook-observer\\api_response_{api_url.split('/')[-1]}.json", "w", encoding="utf-8") as f:
                            json.dump(data, f, indent=2)
                    except:
                        print("  Response is not JSON")
            except Exception as e:
                print(f"  Error: {e}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze()
