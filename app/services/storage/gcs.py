from typing import BinaryIO

from app.services.storage.interfaces import StorageProvider


class GCSStorageProvider(StorageProvider):
    def __init__(self, bucket_name: str, project: str | None = None):
        from google.cloud import storage
        self.client = storage.Client(project=project)
        self.bucket = self.client.bucket(bucket_name)

    def upload(self, key: str, stream: BinaryIO, content_type: str | None = None) -> str:
        blob = self.bucket.blob(key)
        blob.upload_from_file(stream, content_type=content_type)
        return f"gs://{self.bucket.name}/{key}"

    def download(self, key: str) -> bytes:
        return self.bucket.blob(key).download_as_bytes()

    def delete(self, key: str) -> None:
        self.bucket.blob(key).delete()
