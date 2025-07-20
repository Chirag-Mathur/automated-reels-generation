import feedparser
import requests
from bs4 import BeautifulSoup
from app.utils.logger import logger

def fetch_rss_articles(rss_url, max_results=5):
    """Fetch articles from an RSS feed."""
    feed = feedparser.parse(rss_url)
    articles = []
    for entry in feed.entries[:max_results]:
        articles.append({
            "title": entry.get("title", ""),
            "link": entry.get("link", ""),
            "published": entry.get("published", ""),
            "summary": entry.get("summary", ""),
        })
    return articles

def scrape_article_content(url):
    """Scrape the main content from a news article URL."""
    try:
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.content, "html.parser")
        paragraphs = soup.find_all('p')
        article_text = "\n".join([p.get_text() for p in paragraphs])
        return article_text.strip()
    except Exception as e:
        logger.error(f"Error scraping {url}: {e}")
        return "" 