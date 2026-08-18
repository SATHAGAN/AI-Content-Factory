from __future__ import annotations

from app.services.storage.local import LocalStorageBackend, LocalStorageProvider
from app.services.storage.mock_cloud import MockCloudStorageBackend
from app.services.storage.models import StorageConfig,StorageProvider


def create_storage(config: StorageConfig):
    if config.provider == StorageProvider.LOCAL:
        return LocalStorageProvider(
            root=config.root_prefix,
        )

    if config.provider in {
        StorageProvider.GOOGLE_DRIVE,
        StorageProvider.GOOGLE_CLOUD_STORAGE,
    }:
        # The actual cloud connector is intentionally injected separately.
        # Tests use a deterministic mock backend.
        return MockCloudStorageBackend(
            provider=config.provider.value,
            bucket=config.bucket or "configured-storage",
        )

    raise ValueError(f"Unsupported storage provider: {config.provider}")


# Backward-compatible factory used by the existing artifact service.
def get_storage(provider=None, **kwargs):
    from app.services.storage.models import StorageConfig, StorageProvider
    if provider is None:
        provider = StorageProvider.LOCAL
    elif isinstance(provider, str):
        provider = StorageProvider(provider)
    return create_storage(StorageConfig(
        provider=provider,
        bucket=kwargs.get("bucket"),
        root_prefix=kwargs.get("root_prefix", "artifacts/storage"),
    ))
