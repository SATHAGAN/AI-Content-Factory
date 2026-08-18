from __future__ import annotations

import shutil
from pathlib import Path

from app.services.storage.interface import StorageBackend
from app.services.storage.models import (
    DownloadRequest,
    StorageObject,
    UploadRequest,
)


class LocalStorageBackend(StorageBackend):
    def __init__(self, root: str = "artifacts/storage"):
        self.root=Path(root)
        self.root.mkdir(parents=True,exist_ok=True)

    def _safe_path(self,key: str) -> Path:
        candidate=(self.root/key).resolve()
        root=self.root.resolve()
        if root != candidate and root not in candidate.parents:
            raise ValueError("Storage key escapes storage root")
        return candidate

    def upload(self, request: UploadRequest) -> StorageObject:
        source=Path(request.local_path)
        if not source.is_file():
            raise FileNotFoundError(source)

        target=self._safe_path(request.key)
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source,target)

        return StorageObject(
            key=request.key,
            uri=self.uri(request.key),
            size_bytes=target.stat().st_size,
            content_type=request.content_type,
            metadata=dict(request.metadata),
        )

    def download(self, request: DownloadRequest) -> str:
        source=self._safe_path(request.key)
        if not source.is_file():
            raise FileNotFoundError(source)

        target=Path(request.local_path)
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source,target)
        return str(target)

    def exists(self,key: str) -> bool:
        return self._safe_path(key).is_file()

    def delete(self,key: str) -> bool:
        target=self._safe_path(key)
        if not target.exists():
            return False
        target.unlink()
        return True

    def uri(self,key: str) -> str:
        return f"local://{key}"



class LocalStorageProvider(LocalStorageBackend):
    """Legacy byte-stream API retained for earlier phases."""

    def upload(self, key, stream=None, content_type=None):
        from tempfile import NamedTemporaryFile

        if isinstance(stream, UploadRequest):
            return super().upload(stream).uri

        if stream is None:
            raise TypeError("stream is required")

        target=self._safe_path(key)
        target.parent.mkdir(parents=True,exist_ok=True)
        with NamedTemporaryFile(delete=False) as temp:
            temp.write(stream.read())
            temp_path=Path(temp.name)

        try:
            obj=super().upload(UploadRequest(
                key=key,
                local_path=str(temp_path),
                content_type=content_type or "application/octet-stream",
            ))
        finally:
            temp_path.unlink(missing_ok=True)

        return f"file://{self._safe_path(key)}"

    def download(self, request, local_path=None):
        if isinstance(request, DownloadRequest):
            return super().download(request)

        source=self._safe_path(request)
        if local_path is None:
            return source.read_bytes()
        return super().download(DownloadRequest(
            key=request,
            local_path=local_path,
        ))

    def delete(self,key):
        return super().delete(key)


class LocalObjectStorage(LocalStorageProvider):
    """Legacy file-oriented storage API."""

    def put(self, local_path: str, key: str, metadata: dict | None=None):
        obj=LocalStorageBackend.upload(
            self,
            UploadRequest(
                key=key,
                local_path=local_path,
                content_type=(metadata or {}).get(
                    "content_type","application/octet-stream"
                ),
                metadata=metadata or {},
            ),
        )
        return obj

    def get(self,key: str,local_path: str):
        return super().download(key,local_path)
