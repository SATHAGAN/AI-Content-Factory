from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class StorageProvider(str, Enum):
    LOCAL="local"
    GOOGLE_DRIVE="google_drive"
    GOOGLE_CLOUD_STORAGE="google_cloud_storage"


@dataclass(frozen=True)
class StorageObject:
    key: str
    uri: str
    size_bytes: int
    content_type: str = "application/octet-stream"
    metadata: dict = field(default_factory=dict)
    provider: str | None = None


@dataclass(frozen=True)
class UploadRequest:
    key: str
    local_path: str
    content_type: str = "application/octet-stream"
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class DownloadRequest:
    key: str
    local_path: str


@dataclass(frozen=True)
class StorageConfig:
    provider: StorageProvider
    bucket: str | None = None
    root_prefix: str = "ai-content-factory"
