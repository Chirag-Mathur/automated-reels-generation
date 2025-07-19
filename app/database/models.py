from typing import List, Optional, Literal, Union
from datetime import datetime
from pydantic import BaseModel, Field

class ScriptSlide(BaseModel):
    """Represents a single slide in the video script."""
    slide: int
    text: str
    image_query: str
    start_ms: int
    end_ms: int

class UnifiedNewsDoc(BaseModel):
    """
    Pydantic model for the unified MongoDB document schema used in the autonomous video generation pipeline.
    Mirrors the schema and status conventions described in the PRD.
    Note: 'domain' is a free-form string and not a fixed enum; values can be changed or extended as needed.
    """
    _id: Optional[str] = None
    headline: str
    article: str
    domain: str  # Domain is not fixed; can be changed/extended
    source: str
    published_at: datetime
    # Pipeline Meta
    status: str  # Use enums below for allowed values
    relevancy: Optional[int] = None
    sentiment: Optional[Literal["positive", "neutral", "negative"]] = None
    video_title: Optional[str] = None
    hashtags: Optional[List[str]] = None
    caption: Optional[str] = None
    script: Optional[List[ScriptSlide]] = None
    image_urls: Optional[List[str]] = None
    voiceover_url: Optional[str] = None
    video_url: Optional[str] = None
    youtube_id: Optional[str] = None
    instagram_id: Optional[str] = None
    # Error Handling
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    error_at: Optional[datetime] = None

    class Config:
        schema_extra = {
            "example": {
                "headline": "India clinches test series 2-1",
                "article": "Full article text...",
                "domain": "Sports",
                "source": "The Hindu",
                "published_at": "2025-07-18T10:00:00Z",
                "status": "POSTED",
                "relevancy": 8,
                "sentiment": "positive",
                "video_title": "Historic Win for Team India!",
                "hashtags": ["#Cricket", "#TeamIndia"],
                "caption": "A historic win!",
                "script": [
                    {
                        "slide": 1,
                        "text": "India wins the series!",
                        "image_query": "Indian cricket team celebrating",
                        "start_ms": 0,
                        "end_ms": 4000
                    }
                ],
                "image_urls": ["https://.../img1.jpg"],
                "voiceover_url": "https://.../voice.mp3",
                "video_url": "https://.../video.mp4",
                "youtube_id": "abc123",
                "instagram_id": "179834...",
                "error_type": None,
                "error_message": None,
                "error_at": None
            }
        }

# Status enums for reference (not enforced by Pydantic, but for code clarity)
STATUS_SUCCESS = [
    "FETCHED",
    "VALID_ARTICLE",
    "INVALID_ARTICLE",
    "SCRIPT_GENERATED",
    "IMAGES_CREATED",
    "VIDEO_GENERATED",
    "POSTED"
]
STATUS_ERROR = [
    "ERROR_FETCH",
    "ERROR_VALIDATE",
    "ERROR_SCRIPT",
    "ERROR_IMAGES",
    "ERROR_VIDEO",
    "ERROR_POST"
] 