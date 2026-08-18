from pathlib import Path

from app.services.storage.mock_cloud import MockCloudStorageBackend
from app.services.storage.models import UploadRequest,DownloadRequest


def test_mock_google_drive_roundtrip(tmp_path):
    source=tmp_path/"final.mp4"
    source.write_bytes(b"fake-video")

    backend=MockCloudStorageBackend(
        provider="google_drive",
        bucket="drive-root",
    )

    obj=backend.upload(UploadRequest(
        key="channel/job/video/final.mp4",
        local_path=str(source),
        content_type="video/mp4",
        metadata={"job_id":"job"},
    ))

    assert obj.uri.startswith("google_drive://")
    assert backend.exists(obj.key)

    target=tmp_path/"copy.mp4"
    backend.download(DownloadRequest(
        key=obj.key,
        local_path=str(target),
    ))
    assert target.read_bytes()==b"fake-video"
