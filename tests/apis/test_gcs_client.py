import os
import pytest
from app.apis.gcs_client import GCSClient

@pytest.mark.skipif(
    not (os.getenv('GCP_SERVICE_ACCOUNT_JSON') or os.getenv('GOOGLE_APPLICATION_CREDENTIALS')),
    reason="No GCP credentials set in environment."
)
def test_gcs_client_properties():
    """
    Test that GCSClient sets credentials and bucket properties correctly from environment/config.
    This test does not mock and will fail if credentials are not set up.
    """
    client = GCSClient()
    # Check credentials object
    assert client.credentials is not None, "Credentials should be set."
    # Check bucket object
    assert client.bucket is not None, "Bucket should be set."
    # Print for manual verification
    print(f"Credentials type: {type(client.credentials)}")
    print(f"Bucket name: {client.bucket.name}") 