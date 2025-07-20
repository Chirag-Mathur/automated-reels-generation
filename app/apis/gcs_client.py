import os
from google.cloud import storage
from google.oauth2 import service_account

# Path to your service account key file
SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'gen-lang-client-0358368686-dec7ce5b2e58.json')

# Set your bucket name here
GCS_BUCKET_NAME = os.environ.get('GCS_BUCKET_NAME', 'YOUR_BUCKET_NAME')

class GCSClient:
    def __init__(self, bucket_name: str = GCS_BUCKET_NAME, credentials_path: str = SERVICE_ACCOUNT_FILE):
        self.credentials = service_account.Credentials.from_service_account_file(credentials_path)
        self.client = storage.Client(credentials=self.credentials)
        self.bucket = self.client.bucket(bucket_name)

    def upload_file(self, file_path: str, destination_blob_name: str) -> str:
        """
        Uploads a file to the bucket and returns the public URL.
        :param file_path: Path to the file to upload.
        :param destination_blob_name: The destination name of the file in the bucket.
        :return: Public URL of the uploaded file.
        """
        blob = self.bucket.blob(destination_blob_name)
        blob.upload_from_filename(file_path)
        # Construct public URL manually (no need to use blob.public_url which sometimes fails)
        public_url = f"https://storage.googleapis.com/{self.bucket.name}/{destination_blob_name}"
        
        return public_url