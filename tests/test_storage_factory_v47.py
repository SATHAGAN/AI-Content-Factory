from app.services.storage.factory import create_storage
from app.services.storage.local import LocalStorageBackend
from app.services.storage.models import StorageConfig,StorageProvider


def test_factory_local(tmp_path):
    backend=create_storage(StorageConfig(
        provider=StorageProvider.LOCAL,
        root_prefix=str(tmp_path/"local"),
    ))
    assert isinstance(backend,LocalStorageBackend)


def test_factory_google_drive_uses_cloud_boundary():
    backend=create_storage(StorageConfig(
        provider=StorageProvider.GOOGLE_DRIVE,
        bucket="drive-root",
    ))
    assert backend.provider=="google_drive"
