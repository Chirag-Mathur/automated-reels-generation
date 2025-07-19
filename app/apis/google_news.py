import requests
from typing import List, Dict, Optional
from app.utils.logger import logger
from app.config.settings import GOOGLE_SEARCH_API_KEY, GOOGLE_SEARCH_CX

def fetch_google_custom_search(query: str, max_results: int = 5) -> list:
    """
    Fetch news headlines using Google Custom Search API.
    Returns a list of dicts with 'title', 'snippet', and 'displayLink'.
    """
    if not GOOGLE_SEARCH_API_KEY or not GOOGLE_SEARCH_CX:
        raise RuntimeError("Google Custom Search API credentials not set in settings.")

    search_url = (
        f"https://www.googleapis.com/customsearch/v1"
        f"?q={query.replace(' ', '%20')}"
        f"&key={GOOGLE_SEARCH_API_KEY}"
        f"&cx={GOOGLE_SEARCH_CX}"
        f"&sort=date"
        f"&num={max_results}"
        f"&gl=in"
        f"&hl=en"
    )
    try:
        response = requests.get(search_url, timeout=10)
        response.raise_for_status()
        results = response.json()
        return results.get('items', [])
    except requests.RequestException as e:
        print(f"!! An error occurred fetching news for query '{query}': {e}")
        return [] 