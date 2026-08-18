from __future__ import annotations

from pathlib import Path

from app.services.storage.interface import StorageBackend
from app.services.storage.models import (
    DownloadRequest,
    StorageObject,
    UploadRequest,
)


class MockCloudStorageBackend(StorageBackend):
    """Deterministic cloud-like backend used in tests.

    It deliberately performs no external network calls.
    """

    def __init__(self, provider: str="google_drive", bucket: str="test-bucket"):
        self.provider=provider
        self.bucket=bucket
        self.objects={}

    def upload(self, request: UploadRequest) -> StorageObject:
        path=Path(request.local_path)
        if not path.is_file():
            raise FileNotFoundError(path)
        data=path.read_bytes()
        obj=StorageObject(
            key=request.key,
            uri=self.uri(request.key),
            size_bytes=len(data),
            content_type=request.content_type,
            metadata=dict(request.metadata),
        )
        self.objects[request.key]=(data,obj)
        return obj

    def download(self, request: DownloadRequest) -> str:
        if request.key not in self.objects:
            raise FileNotFoundError(request.key)
        data,_=self.objects[request.key]
        target=Path(request.local_path)
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(data)
        return str(target)

    def exists(self,key: str) -> bool:
        return key in self.objects

    def delete(self,key: str) -> bool:
        return self.objects.pop(key,None) is not None

    def uri(self,key: str) -> str:
        return f"{self.provider}://{self.bucket}/{key}"
