import os
from datetime import datetime
from app.database.mongo import get_collection
from app.media.ffmpeg_utils import generate_video_with_overlay_and_caption
from app.utils.logger import logger
from app.apis.gcs_client import GCSClient

NEWS_COLLECTION = 'news'
VIDEO_RESOLUTION = "1080x1920"
# FONT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media', 'fonts', 'Montserrat-SemiBold.ttf')
# BACKGROUND_VIDEO_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media', 'background_video')
# BACKGROUND_MUSIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media', 'background_music')
# OUTPUTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'outputs')

# We're inside /app/app/pipelines/
# So go TWO levels up to reach /app/app/
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))

FONT_PATH = os.path.join(BASE_DIR, 'media', 'fonts', 'Montserrat-SemiBold.ttf')
BACKGROUND_VIDEO_DIR = os.path.join(BASE_DIR, 'media', 'background_video')
BACKGROUND_MUSIC_DIR = os.path.join(BASE_DIR, 'media', 'background_music')
OUTPUTS_DIR = os.path.join(BASE_DIR, 'outputs')  # outputs is inside /app/app/


def get_background_video(domain: str, sentiment: str) -> str:
    domain = domain.lower()
    sentiment = sentiment.lower()
    video_path = os.path.join(BACKGROUND_VIDEO_DIR, domain, sentiment, f"{sentiment}_{domain}.mp4")
    if os.path.exists(video_path):
        return video_path
    logger.warning(f"Background video not found for {domain}/{sentiment}, using fallback.")
    # Fallback: pick any video in the domain/sentiment folder
    folder = os.path.join(BACKGROUND_VIDEO_DIR, domain, sentiment)
    for f in os.listdir(folder):
        if f.endswith('.mp4'):
            return os.path.join(folder, f)
    raise FileNotFoundError(f"No background video found for {domain}/{sentiment}")

def get_background_music(sentiment: str) -> str:
    sentiment = sentiment.lower()
    music_path = os.path.join(BACKGROUND_MUSIC_DIR, f"{sentiment}.mp3")
    if os.path.exists(music_path):
        return music_path
    raise FileNotFoundError(f"No background music found for sentiment {sentiment}")

def safe_filename(name: str) -> str:
    return "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in name).strip().replace(' ', '_')

def process_script_generated_articles():
    collection = get_collection(NEWS_COLLECTION)
    if collection is None:
        logger.error("Could not get MongoDB collection 'news'. Skipping processing.")
        return
    articles = list(collection.find({"status": "SCRIPT_GENERATED"}).sort([("relevancy", -1)]).limit(2))
    logger.info(f"Found {len(articles)} articles with status SCRIPT_GENERATED ")
    for doc in articles:
        doc_id = doc["_id"]
        domain = doc.get("domain", "entertainment")
        sentiment = doc.get("sentiment", "neutral")
        caption = doc.get("caption", "")
        video_title = doc.get("video_title", f"video_{doc_id}")
        try:
            video_path = get_background_video(domain, sentiment)
            music_path = get_background_music(sentiment)
            today = datetime.now().strftime('%Y-%m-%d')
            output_dir = os.path.join(OUTPUTS_DIR, today)
            os.makedirs(output_dir, exist_ok=True)
            output_filename = safe_filename(video_title) + ".mp4"
            output_path = os.path.join(output_dir, output_filename)
            generate_video_with_overlay_and_caption(
                background_video_path=video_path,
                background_music_path=music_path,
                font_path=FONT_PATH,
                caption=caption,
                output_path=output_path,
                resolution=VIDEO_RESOLUTION
            )
            # Upload to GCS
            gcs_client = GCSClient()
            relative_local_path = os.path.relpath(output_path, start=os.path.dirname(os.path.dirname(__file__)))
            gcs_blob_name = f"videos/{today}/{output_filename}"
            public_url = gcs_client.upload_file(output_path, gcs_blob_name)
            # Update DB
            collection.update_one({"_id": doc_id}, {"$set": {
                "video_url": public_url,
                "video_local_path": relative_local_path,
                "status": "VIDEO_GENERATED",
                "error_message": None,
                "error_type": None,
                "error_at": None,
                "mod_at": datetime.utcnow()
            }})
            logger.info(f"Video generated and uploaded for article '{video_title}' at {public_url}")
        except Exception as e:
            logger.error(f"Video generation failed for '{video_title}': {e}")
            collection.update_one({"_id": doc_id}, {"$set": {
                "status": "ERROR_VIDEO",
                "error_message": str(e),
                "error_type": "VIDEO_GENERATION_ERROR",
                "error_at": datetime.utcnow(),
                "mod_at": datetime.utcnow()
            }})

if __name__ == "__main__":
    process_script_generated_articles() 
