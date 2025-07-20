import requests
from app.config import settings
import os
from app.utils.logger import logger
import time

class InstagramAPIError(Exception):
    """Custom exception for Instagram API errors."""
    pass

def wait_for_media_ready(container_id, access_token, max_wait=180, poll_interval=3):
    status_url = f"https://graph.facebook.com/v23.0/{container_id}"
    params = {
        "fields": "status_code",
        "access_token": access_token
    }
    waited = 0
    while waited < max_wait:
        resp = requests.get(status_url, params=params)
        logger.info(f"Polling media status: {resp.status_code} {resp.text}")
        try:
            resp.raise_for_status()
        except Exception as e:
            logger.error(f"Error polling media status: {e}")
            raise InstagramAPIError(f"Error polling media status: {e}")
        status = resp.json().get("status_code")
        if status == "FINISHED":
            return True
        elif status == "ERROR":
            raise InstagramAPIError(f"Media processing failed: {resp.text}")
        time.sleep(poll_interval)
        waited += poll_interval
    raise InstagramAPIError("Timed out waiting for media to be ready for publishing.")

def post_reel_to_instagram(video_url: str, caption: str) -> str:
    """
    Uploads a reel to Instagram using the provided public video URL and caption.
    Returns the published Instagram post ID on success.
    Raises InstagramAPIError on failure.
    """
    ig_user_id = os.getenv('INSTAGRAM_USER_ID') or getattr(settings, 'INSTAGRAM_USER_ID', None)
    access_token = settings.INSTAGRAM_ACCESS_TOKEN
    if not ig_user_id or not access_token:
        raise InstagramAPIError("Instagram user ID or access token not set in environment variables.")

    # Step 1: Create media container
    container_url = f"https://graph.facebook.com/v23.0/{ig_user_id}/media"
    container_payload = {
        'video_url': video_url,
        'caption': caption,
        'media_type': 'REELS',
        'access_token': access_token
    }
    try:
        container_resp = requests.post(container_url, data=container_payload)
        logger.info(f"Instagram container response: {container_resp.status_code} {container_resp.text}")
        container_resp.raise_for_status()
        container_data = container_resp.json()
        container_id = container_data.get('id')
        if not container_id:
            logger.error(f"Failed to create media container: {container_data}")
            raise InstagramAPIError(f"Failed to create media container: {container_data}")
    except Exception as e:
        logger.error(f"Error creating Instagram media container: {e}")
        raise InstagramAPIError(f"Error creating Instagram media container: {e}")

    # Step 1.5: Poll for media readiness (max 3 minutes)
    try:
        wait_for_media_ready(container_id, access_token, max_wait=180, poll_interval=3)
    except Exception as e:
        logger.error(f"Media not ready for publishing: {e}")
        raise InstagramAPIError(f"Media not ready for publishing: {e}")

    # Step 2: Publish the container
    publish_url = f"https://graph.facebook.com/v23.0/{ig_user_id}/media_publish"
    publish_payload = {
        'creation_id': container_id,
        'access_token': access_token
    }
    try:
        publish_resp = requests.post(publish_url, data=publish_payload)
        logger.info(f"Instagram publish response: {publish_resp.status_code} {publish_resp.text}")
        publish_resp.raise_for_status()
        publish_data = publish_resp.json()
        published_id = publish_data.get('id')
        if not published_id:
            logger.error(f"Failed to publish media: {publish_data}")
            raise InstagramAPIError(f"Failed to publish media: {publish_data}")
        return published_id
    except Exception as e:
        logger.error(f"Error publishing Instagram media: {e}")
        raise InstagramAPIError(f"Error publishing Instagram media: {e}") 