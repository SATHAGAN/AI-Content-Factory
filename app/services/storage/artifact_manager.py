from __future__ import annotations

from pathlib import Path

from app.services.storage.models import UploadRequest


class ArtifactManager:
    """Canonical artifact naming for production outputs."""

    def __init__(self, backend):
        self.backend=backend

    def key(self, *, channel_id: str, job_id: str, kind: str, filename: str) -> str:
        safe_channel=channel_id.replace("/","_")
        safe_job=job_id.replace("/","_")
        safe_kind=kind.replace("/","_")
        safe_name=Path(filename).name
        return f"{safe_channel}/{safe_job}/{safe_kind}/{safe_name}"

    def upload_file(
        self,
        *,
        channel_id: str,
        job_id: str,
        kind: str,
        local_path: str,
        content_type: str,
        metadata: dict | None=None,
    ):
        key=self.key(
            channel_id=channel_id,
            job_id=job_id,
            kind=kind,
            filename=Path(local_path).name,
        )
        return self.backend.upload(
            UploadRequest(
                key=key,
                local_path=local_path,
                content_type=content_type,
                metadata=metadata or {},
            )
        )
