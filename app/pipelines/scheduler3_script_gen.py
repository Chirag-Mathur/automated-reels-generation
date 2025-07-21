import os
import json
from datetime import datetime
from app.database.mongo import get_collection
from app.ai.gemini_client import gemini_generate_content
from app.utils.logger import logger

RESOURCES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources')
PROMPT_PATH = os.path.join(RESOURCES_DIR, 'gemini_script_prompt.txt')

NEWS_COLLECTION = 'news'


def load_prompt_template() -> str:
    with open(PROMPT_PATH, 'r') as f:
        return f.read()

def build_prompt(headline: str, article: str) -> str:
    template = load_prompt_template()
    return template.replace('{headline}', headline).replace('{article}', article)

def parse_gemini_script_response(result: dict) -> dict:
    # Expects Gemini to return a JSON object as text in result['candidates'][0]['content']['parts'][0]['text']
    if not result or 'candidates' not in result or not result['candidates']:
        return {"error": "No response from Gemini API."}
    try:
        text = result['candidates'][0]['content']['parts'][0]['text']
        text = text.strip()
        if text.startswith('```json'):
            text = text[len('```json'):].strip()
        if text.startswith('```'):
            text = text[len('```'):].strip()
        if text.endswith('```'):
            text = text[:-len('```')].strip()
        return json.loads(text)
    except Exception as e:
        logger.error(f"Raw Gemini response text: {text}")
        return {"error": f"Failed to parse Gemini response: {e}", "raw_text": text, "raw_result": result}

def update_article_status(doc_id, status, message, error_type=None):
    collection = get_collection(NEWS_COLLECTION)
    if collection is None:
        logger.error("Could not get MongoDB collection 'news'. Skipping update.")
        return
    update = {
        "$set": {
            "status": status,
            "error_message": message,
            "error_type": error_type,
            "error_at": datetime.utcnow(),
            "mod_at": datetime.utcnow()
        }
    }
    collection.update_one({"_id": doc_id}, update)

def process_valid_articles():
    collection = get_collection(NEWS_COLLECTION)
    if collection is None:
        logger.error("Could not get MongoDB collection 'news'. Skipping processing.")
        return
    # Get top 10 articles sorted by relevancy desc, then created_at desc
    valid_articles = list(collection.find({"status": {"$in": ["VALID_ARTICLE", "ERROR_SCRIPT"]}}).sort([
        ("relevancy", -1), ("created_at", -1)
    ]).limit(10))
    logger.info(f"Found {len(valid_articles)} articles with status VALID_ARTICLE or ERROR_SCRIPT ")
    for doc in valid_articles:
        doc_id = doc["_id"]
        headline = doc.get("headline", "")
        article = doc.get("article", "")
        logger.info(f"Generating script for article: {headline}")
        prompt = build_prompt(headline, article)
        result = gemini_generate_content(prompt)
        if result is None:
            update_article_status(doc_id, "ERROR_SCRIPT", "No response from Gemini API.", error_type="GEMINI_SCRIPT_ERROR")
            logger.error(f"Script generation failed for '{headline}': No response from Gemini API.")
            continue
        parsed = parse_gemini_script_response(result)
        if "error" in parsed:
            update_article_status(doc_id, "ERROR_SCRIPT", parsed["error"], error_type="GEMINI_SCRIPT_ERROR")
            logger.error(f"Script generation failed for '{headline}': {parsed['error']}")
            continue
        # Validate required fields
        required_fields = ["sentiment", "video_title", "hashtags", "caption"]
        if not all(field in parsed for field in required_fields):
            update_article_status(doc_id, "ERROR_SCRIPT", f"Missing fields in Gemini response: {parsed}", error_type="GEMINI_SCRIPT_MISSING_FIELDS")
            logger.error(f"Missing fields in Gemini response for '{headline}': {parsed}")
            continue
        # Update document with script data
        update = {
            "$set": {
                "sentiment": parsed["sentiment"],
                "video_title": parsed["video_title"],
                "hashtags": parsed["hashtags"],
                "caption": parsed["caption"],
                "status": "SCRIPT_GENERATED",
                "error_message": None,
                "error_type": None,
                "error_at": None,
                "mod_at": datetime.utcnow()
            }
        }
        collection.update_one({"_id": doc_id}, update)
        logger.info(f"Script generated and updated for article '{headline}'.")

if __name__ == "__main__":
    process_valid_articles() 