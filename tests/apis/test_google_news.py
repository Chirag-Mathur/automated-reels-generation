# import pytest
# from unittest.mock import patch
# from app.apis.google_news import fetch_google_custom_search

# @pytest.fixture
# def mock_good_response():
#     return {
#         "status": "ok",
#         "articles": [
#             {"title": "Headline 1", "content": "Article 1 content."},
#             {"title": "Headline 2", "content": "Article 2 content."}
#         ]
#     }

# @pytest.fixture
# def mock_empty_response():
#     return {"status": "ok", "articles": []}

# @patch("app.apis.google_news.requests.get")
# def test_fetch_google_news_success(mock_get, mock_good_response):
#     class MockResp:
#         def raise_for_status(self):
#             pass
#         def json(self):
#             return mock_good_response
#     mock_get.return_value = MockResp()
#     results = fetch_google_custom_search("test")
#     assert isinstance(results, list)
#     assert len(results) == 2
#     assert all("headline" in doc and "article" in doc for doc in results)
#     assert results[0]["headline"] == "Headline 1"
#     assert results[1]["article"] == "Article 2 content."

# @patch("app.apis.google_news.requests.get")
# def test_fetch_google_news_empty(mock_get, mock_empty_response):
#     class MockResp:
#         def raise_for_status(self):
#             pass
#         def json(self):
#             return mock_empty_response
#     mock_get.return_value = MockResp()
#     results = fetch_google_custom_search("test")
#     assert isinstance(results, list)
#     assert results == []

# @patch("app.apis.google_news.requests.get")
# def test_fetch_google_news_api_error(mock_get):
#     mock_get.side_effect = Exception("API down")
#     results = fetch_google_custom_search("test")
#     assert results == []

# def test_fetch_google_news_no_api_key(monkeypatch):
#     monkeypatch.setenv("GOOGLE_NEWS_API_KEY", "")
#     results = fetch_google_custom_search("test")
#     assert results == [] 