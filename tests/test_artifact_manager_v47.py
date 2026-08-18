from pathlib import Path

from app.services.storage.artifact_manager import ArtifactManager
from app.services.storage.mock_cloud import MockCloudStorageBackend


def test_artifact_manager_uses_stable_layout(tmp_path):
    source=tmp_path/"final.mp4"
    source.write_bytes(b"data")

    manager=ArtifactManager(MockCloudStorageBackend())
    obj=manager.upload_file(
        channel_id="kids-stories",
        job_id="job-123",
        kind="video",
        local_path=str(source),
        content_type="video/mp4",
        metadata={"platform":"youtube"},
    )

    assert obj.key=="kids-stories/job-123/video/final.mp4"
    assert obj.metadata["platform"]=="youtube"
