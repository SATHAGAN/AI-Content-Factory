from __future__ import annotations

from pathlib import Path
from typing import BinaryIO

from app.services.storage.factory import get_storage


class ArtifactStore:
    """Application-level artifact storage facade.

    The underlying provider can be local storage or Google Cloud Storage.
    """

    def __init__(self, provider=None):
        self.provider = provider or get_storage()

    def put_file(self, key: str, path: str | Path, content_type: str | None = None) -> str:
        with Path(path).open("rb") as stream:
            return self.provider.upload(key, stream, content_type)

    def put_bytes(self, key: str, data: bytes, content_type: str | None = None) -> str:
        from io import BytesIO
        return self.provider.upload(key, BytesIO(data), content_type)

    def get_bytes(self, key: str) -> bytes:
        return self.provider.download(key)

    def delete(self, key: str) -> None:
        self.provider.delete(key)
