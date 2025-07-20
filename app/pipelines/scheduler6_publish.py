import os
from datetime import datetime
from app.database.mongo import get_collection
from app.utils.logger import logger
from app.apis.instagram import post_reel_to_instagram, InstagramAPIError

NEWS_COLLECTION = 'news'

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

def process_video_generated_articles():
    collection = get_collection(NEWS_COLLECTION)
    if collection is None:
        logger.error("Could not get MongoDB collection 'news'. Skipping processing.")
        return
    articles = list(collection.find({"status": "VIDEO_GENERATED"}).sort([("relevancy", -1)]).limit(1))
    logger.info(f"Found {len(articles)} articles with status VIDEO_GENERATED ")
    for doc in articles:
        doc_id = doc["_id"]
        video_url = doc.get("video_url")
        caption = doc.get("caption", "")
        try:
            if not video_url:
                raise ValueError("No video_url found in document.")
            logger.info(f"Uploading video for doc_id={doc_id} to Instagram...")
            instagram_id = post_reel_to_instagram(video_url, caption)
            collection.update_one({"_id": doc_id}, {"$set": {
                "instagram_id": instagram_id,
                "status": "POSTED",
                "error_message": None,
                "error_type": None,
                "error_at": None,
                "mod_at": datetime.utcnow()
            }})
            logger.info(f"Successfully posted to Instagram for doc_id={doc_id}, instagram_id={instagram_id}")
        except InstagramAPIError as e:
            logger.error(f"Instagram API error for doc_id={doc_id}: {e}")
            update_article_status(doc_id, "ERROR_POST", str(e), error_type="INSTAGRAM_API_ERROR")
        except Exception as e:
            logger.error(f"Unexpected error for doc_id={doc_id}: {e}")
            update_article_status(doc_id, "ERROR_POST", str(e), error_type="UNEXPECTED_ERROR")

if __name__ == "__main__":
    process_video_generated_articles() 