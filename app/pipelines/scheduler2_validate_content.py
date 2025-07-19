import os
import json
from datetime import datetime
from app.database.mongo import get_collection
from app.ai.gemini_client import gemini_generate_content
from app.utils.logger import logger

RESOURCES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources')
PROMPT_PATH = os.path.join(RESOURCES_DIR, 'gemini_validation_prompt.txt')

NEWS_COLLECTION = 'news'


def load_prompt_template() -> str:
    with open(PROMPT_PATH, 'r') as f:
        return f.read()

def build_prompt(headline: str) -> str:
    template = load_prompt_template()
    return template.replace('{headline}', headline)

def validate_article_with_gemini(headline: str) -> dict:
    prompt = build_prompt(headline)
    result = gemini_generate_content(prompt)
    if not result or 'candidates' not in result or not result['candidates']:
        return {"error": "No response from Gemini API."}
    try:
        text = result['candidates'][0]['content']['parts'][0]['text']
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
            "error_at": datetime.utcnow()
        }
    }
    collection.update_one({"_id": doc_id}, update)

def process_fetched_articles():
    collection = get_collection(NEWS_COLLECTION)
    if collection is None:
        logger.error("Could not get MongoDB collection 'news'. Skipping processing.")
        return
    fetched = list(collection.find({"status": "FETCHED"}))
    logger.info(f"Found {len(fetched)} articles with status FETCHED ")
    for doc in fetched:
        doc_id = doc["_id"]
        headline = doc["headline"]
        logger.info(f"Validating article: {headline}")
        result = validate_article_with_gemini(headline)
        if "error" in result:
            update_article_status(doc_id, "ERROR_VALIDATE", result["error"], error_type="GEMINI_VALIDATION_ERROR")
            logger.error(f"Validation failed for '{headline}': {result['error']}")
            continue
        if result.get("valid", "NO") != "YES":
            update_article_status(doc_id, "INVALID_ARTICLE", result.get("reason", "Not valid."))
            logger.info(f"Article '{headline}' marked as INVALID_ARTICLE.")
            continue
        if result.get("related_to_india", "NO") != "YES":
            update_article_status(doc_id, "INVALID_ARTICLE", "Not related to India.")
            logger.info(f"Article '{headline}' not related to India.")
            continue
        # If valid and related to India
        update = {
            "$set": {
                "status": "VALID_ARTICLE",
                "error_message": "Validated successfully.",
                "error_type": None,
                "error_at": None,
                "relevancy": 10,  # Placeholder, can be set by Gemini if needed
            }
        }
        collection.update_one({"_id": doc_id}, update)
        logger.info(f"Article '{headline}' marked as VALID_ARTICLE.")

if __name__ == "__main__":
    process_fetched_articles() 