from flask import Blueprint, jsonify
from datetime import datetime, timedelta
from app.database.mongo import get_collection

TOP_NEWS_FIELDS = [
    "_id", "caption", "created_at", "domain", "headline", "relevancy", "sentiment", "status", "video_url"
]

top_news_bp = Blueprint('top_news', __name__)

@top_news_bp.route("/top_news", methods=["GET"])
def top_news():
    collection = get_collection("news")
    if collection is None:
        return jsonify({"error": "Database connection error"}), 500
    now = datetime.utcnow()
    since = now - timedelta(hours=24)
    # Query: created_at >= since, status in [VIDEO_GENERATED, POSTED]
    query = {
        "created_at": {"$gte": since},
        "status": {"$in": ["VIDEO_GENERATED", "POSTED"]}
    }
    cursor = collection.find(query).sort([
        ("relevancy", -1), ("created_at", -1)
    ]).limit(10)
    docs = []
    for doc in cursor:
        filtered_doc = {k: (str(doc[k]) if k == "_id" else doc.get(k)) for k in TOP_NEWS_FIELDS if k in doc}
        docs.append(filtered_doc)
    return jsonify(docs), 200 