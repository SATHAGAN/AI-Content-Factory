from pathlib import Path

from app.services.storage.local import LocalStorageBackend
from app.services.storage.models import UploadRequest,DownloadRequest


def test_local_upload_download_exists_delete(tmp_path):
    root=tmp_path/"storage"
    source=tmp_path/"video.mp4"
    source.write_bytes(b"video-data")

    backend=LocalStorageBackend(str(root))
    obj=backend.upload(UploadRequest(
        key="jobs/job1/video/final.mp4",
        local_path=str(source),
        content_type="video/mp4",
    ))

    assert obj.size_bytes==len(b"video-data")
    assert backend.exists(obj.key)

    target=tmp_path/"downloaded.mp4"
    backend.download(DownloadRequest(
        key=obj.key,
        local_path=str(target),
    ))
    assert target.read_bytes()==b"video-data"

    assert backend.delete(obj.key)
    assert not backend.exists(obj.key)


def test_local_storage_rejects_path_traversal(tmp_path):
    backend=LocalStorageBackend(str(tmp_path/"storage"))
    source=tmp_path/"a.txt"
    source.write_text("x")
    try:
        backend.upload(UploadRequest(
            key="../../outside.txt",
            local_path=str(source),
        ))
    except ValueError:
        pass
    else:
        raise AssertionError("Path traversal must be rejected")
