from io import BytesIO

from app.services.storage.local import LocalStorageProvider


def test_local_storage_round_trip(tmp_path):
    storage = LocalStorageProvider(str(tmp_path))
    uri = storage.upload("tenant/a.txt", BytesIO(b"hello"), "text/plain")
    assert uri.startswith("file://")
    assert storage.download("tenant/a.txt") == b"hello"
    storage.delete("tenant/a.txt")
    assert not (tmp_path / "tenant" / "a.txt").exists()


def test_local_storage_blocks_path_traversal(tmp_path):
    storage = LocalStorageProvider(str(tmp_path))
    try:
        storage.download("../secret.txt")
    except ValueError:
        pass
    else:
        raise AssertionError("Path traversal should be rejected")
