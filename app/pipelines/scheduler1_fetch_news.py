# Scheduler 1: News Fetch logic 
import os
import json
from datetime import datetime, timedelta
from typing import List, Dict
from app.database.models import UnifiedNewsDoc
from app.database.mongo import get_collection
from app.config import settings
import requests
from app.apis.google_news import fetch_google_custom_search
from app.utils.logger import logger
from app.utils.rss_utils import fetch_rss_articles, scrape_article_content

RESOURCES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources')
QUERIES_PATH = os.path.join(RESOURCES_DIR, 'news_queries.json')

# Define the 5 domains and their queries
NEWS_DOMAINS = {
    "entertainment": "latest entertainment news India after:{date}",
    "finance": "latest finance news India after:{date}",
    "politics": "latest politics news India after:{date}",
    "sports": "latest sports news India after:{date}",
    "tech": "latest technology news India after:{date}"
}

def ensure_resources_and_queries():
    """Ensure resources directory and queries file exist, and write queries if not present."""
    os.makedirs(RESOURCES_DIR, exist_ok=True)
    if not os.path.exists(QUERIES_PATH):
        # Use RFC3339 date for Google Search API (YYYY-MM-DD)
        date_6h_ago = (datetime.utcnow() - timedelta(hours=6)).strftime('%Y-%m-%d')
        queries = {domain: query.format(date=date_6h_ago) for domain, query in NEWS_DOMAINS.items()}
        with open(QUERIES_PATH, 'w') as f:
            json.dump(queries, f, indent=2)
    else:
        with open(QUERIES_PATH, 'r') as f:
            queries = json.load(f)
    return queries

def fetch_news_for_domain(domain: str, query: str, max_results: int = 5) -> List[Dict]:
    """Fetch news using fetch_google_custom_search for a given domain query."""
    logger.info(f"Fetching news for domain '{domain}' with query: {query}")
    news_items = fetch_google_custom_search(query, max_results=max_results)
    logger.info(f"Fetched {len(news_items)} news items for domain '{domain}'")
    return news_items

def store_news_in_db(news_items: List[Dict], domain: str):
    """Store each news item as a UnifiedNewsDoc in MongoDB with status FETCHED."""
    collection = get_collection("news")
    if collection is None:
        logger.warning("Could not get MongoDB collection 'news'. Skipping DB insert.")
        return
    for item in news_items:
        doc = UnifiedNewsDoc(
            headline=item.get("title", ""),
            article=item.get("snippet", ""),
            domain=domain.capitalize(),
            source=item.get("displayLink", ""),
            published_at=datetime.utcnow(),
            status="FETCHED"
        )
        # Insert as dict, omitting None fields
        collection.insert_one({k: v for k, v in doc.dict().items() if v is not None})
        logger.info(f"Saved news: '{doc.headline}' for domain '{domain}' to DB.")

def fetch_and_store_all_domains():
    """Fetch and store news for all domains as per queries in resources/news_queries.json."""
    queries = ensure_resources_and_queries()
    for domain, query in queries.items():
        try:
            news_items = fetch_news_for_domain(domain, query)
            store_news_in_db(news_items, domain)
        except Exception as e:
            # Log error and continue
            print(f"Error fetching/storing news for {domain}: {e}") 

def fetch_and_store_rss_news():
    rss_path = os.path.join(RESOURCES_DIR, 'rss_feeds.json')
    with open(rss_path, 'r') as f:
        rss_feeds = json.load(f)
    collection = get_collection("news")
    for feed in rss_feeds:
        source = feed["source"]
        url = feed["url"]
        tags = feed.get("tags", [])
        articles = fetch_rss_articles(url)
        for art in articles:
            full_article = scrape_article_content(art["link"])
            doc = UnifiedNewsDoc(
                headline=art["title"],
                article=full_article or art["summary"],
                domain=", ".join(tags),
                source=source,
                published_at=datetime.utcnow(),
                status="FETCHED"
            )
            if collection is not None:
                collection.insert_one({k: v for k, v in doc.dict().items() if v is not None})
                logger.info(f"Saved RSS news: '{doc.headline}' from '{source}' to DB.")


if __name__ == "__main__":
    # fetch_and_store_all_domains()
    fetch_and_store_rss_news()