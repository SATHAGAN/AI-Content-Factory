from app.services.artifacts.store import ArtifactStore
from app.services.storage.local import LocalStorageProvider


def test_artifact_store_local(tmp_path):
    store = ArtifactStore(LocalStorageProvider(str(tmp_path)))
    uri = store.put_bytes("org/a.txt", b"hello", "text/plain")
    assert uri.startswith("file://")
    assert store.get_bytes("org/a.txt") == b"hello"
