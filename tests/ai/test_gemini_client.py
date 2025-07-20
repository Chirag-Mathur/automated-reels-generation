import pytest
from unittest.mock import patch
import requests
from app.ai.gemini_client import gemini_generate_content

@pytest.fixture
def mock_success_response():
    return {"candidates": [{"content": {"parts": [{"text": "Hello from Gemini!"}]}}]}


def test_gemini_generate_content_success(mock_success_response):
    """
    Test that gemini_generate_content returns a valid response on success.
    """
    class MockResponse:
        def raise_for_status(self):
            pass
        def json(self):
            return mock_success_response
    def mock_post(*args, **kwargs):
        return MockResponse()
    with patch("app.ai.gemini_client.GEMINI_API_KEY", "dummy-key"):
        with patch("requests.post", mock_post):
            result = gemini_generate_content("Hello Gemini!")
            assert result == mock_success_response


def test_gemini_generate_content_no_api_key():
    """
    Test that gemini_generate_content raises RuntimeError if API key is missing.
    """
    with patch("app.ai.gemini_client.GEMINI_API_KEY", None):
        with pytest.raises(RuntimeError):
            gemini_generate_content("Test prompt")


def test_gemini_generate_content_http_error():
    """
    Test that gemini_generate_content returns None on HTTP error after retries.
    """
    class MockResponse:
        def raise_for_status(self):
            raise requests.HTTPError("HTTP error")
    def mock_post(*args, **kwargs):
        return MockResponse()
    with patch("app.ai.gemini_client.GEMINI_API_KEY", "dummy-key"):
        with patch("requests.post", mock_post):
            result = gemini_generate_content("Test error")
            assert result is None 