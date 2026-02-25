import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_scrape():
    url = "https://www.moltbook.com/api/v1/posts?skip=20&limit=20"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.moltbook.com/"
    }
    
    try:
        logger.info(f"Testing connection to {url}...")
        response = requests.get(url, headers=headers, timeout=10)
        logger.info(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            logger.info("Success! First post preview:")
            import json
            logger.info(json.dumps(data['posts'][0], indent=2))
        else:
            logger.error(f"Failed. Response: {response.text[:500]}")
            
    except Exception as e:
        logger.error(f"Exception: {e}")

if __name__ == "__main__":
    test_scrape()
