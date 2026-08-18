from __future__ import annotations

from abc import ABC, abstractmethod

from app.services.storage.models import (
    DownloadRequest,
    StorageObject,
    UploadRequest,
)


class StorageBackend(ABC):
    @abstractmethod
    def upload(self, request: UploadRequest) -> StorageObject:
        raise NotImplementedError

    @abstractmethod
    def download(self, request: DownloadRequest) -> str:
        raise NotImplementedError

    @abstractmethod
    def exists(self, key: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def delete(self, key: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def uri(self, key: str) -> str:
        raise NotImplementedError
