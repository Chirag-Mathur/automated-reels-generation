import requests
from typing import Any, Dict, Optional
from app.config.settings import GEMINI_API_KEY
from app.utils.logger import logger

# GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={}".format(GEMINI_API_KEY)
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={}".format(GEMINI_API_KEY)


def gemini_generate_content(prompt: str, model: str = "gemini-pro", max_retries: int = 3) -> Optional[Dict[str, Any]]:
    """
    Sends a prompt to the Gemini API and returns the generated result.
    Args:
        prompt (str): The prompt to send to Gemini.
        model (str): The Gemini model to use (default: "gemini-pro").
        max_retries (int): Number of retries for transient errors.
    Returns:
        Optional[Dict[str, Any]]: The Gemini API response, or None on failure.
    Raises:
        RuntimeError: If the API key is not set.
    """
    if not GEMINI_API_KEY:
        raise RuntimeError("Gemini API key not set in settings.")

    url = GEMINI_API_URL
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            response.raise_for_status()
            result = response.json()
            logger.info(f"Gemini API call successful (attempt {attempt})")
            return result
        except requests.RequestException as e:
            logger.error(f"Gemini API error (attempt {attempt}): {e}")
            if attempt == max_retries:
                logger.error(f"Gemini API failed after {max_retries} attempts.")
    return None 