import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv('MONGO_URI')
GCP_PROJECT = os.getenv('GCP_PROJECT')
GCS_BUCKET = os.getenv('GCS_BUCKET')
GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
INSTAGRAM_ACCESS_TOKEN = os.getenv('INSTAGRAM_ACCESS_TOKEN') 
GOOGLE_NEWS_API_KEY = os.getenv('GOOGLE_NEWS_API_KEY')  # Google News API key 
GOOGLE_SEARCH_API_KEY = os.getenv('GOOGLE_SEARCH_API_KEY')  # Google Custom Search API key
GOOGLE_SEARCH_CX = os.getenv('GOOGLE_SEARCH_CX')  # Google Custom Search Engine CX 