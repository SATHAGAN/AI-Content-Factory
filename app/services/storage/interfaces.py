from __future__ import annotations

from typing import Protocol

from app.services.storage.models import StorageObject


class ObjectStorage(Protocol):
    provider: str

    def put(self, local_path: str, key: str, metadata: dict | None = None) -> StorageObject:
        ...

    def get(self, key: str, local_path: str) -> str:
        ...

    def delete(self, key: str) -> None:
        ...

    def exists(self, key: str) -> bool:
        ...
