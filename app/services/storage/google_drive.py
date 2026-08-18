from __future__ import annotations

import io
from pathlib import Path

from app.services.storage.models import StorageObject


class GoogleDriveStorage:
    """Google Drive object-storage adapter.

    Authentication is injected so credentials/tokens never live in content
    metadata. A service should expose Drive API v3 `files().create`,
    `files().get_media`, and `files().delete`.
    """

    provider="google-drive"

    def __init__(self, service, parent_folder_id: str):
        if service is None:
            raise ValueError("Google Drive service is required")
        if not parent_folder_id:
            raise ValueError("parent_folder_id is required")
        self.service=service
        self.parent_folder_id=parent_folder_id
        self._ids={}

    def put(self, local_path: str, key: str, metadata: dict | None = None) -> StorageObject:
        try:
            from googleapiclient.http import MediaFileUpload
        except ImportError as exc:
            raise RuntimeError(
                "Install google-api-python-client for Google Drive storage"
            ) from exc

        source=Path(local_path)
        if not source.is_file():
            raise FileNotFoundError(local_path)

        body={
            "name":Path(key).name,
            "parents":[self.parent_folder_id],
            "description":key,
        }
        media=MediaFileUpload(str(source),resumable=True)
        response=self.service.files().create(
            body=body,
            media_body=media,
            fields="id,name,size,webViewLink",
        ).execute()
        self._ids[key]=response["id"]

        return StorageObject(
            key=key,
            uri=response.get("webViewLink") or f"gdrive://{response['id']}",
            size_bytes=int(response.get("size",source.stat().st_size)),
            provider=self.provider,
            metadata={**(metadata or {}),"drive_file_id":response["id"]},
        )

    def get(self,key: str,local_path: str) -> str:
        try:
            from googleapiclient.http import MediaIoBaseDownload
        except ImportError as exc:
            raise RuntimeError(
                "Install google-api-python-client for Google Drive storage"
            ) from exc

        file_id=self._ids.get(key)
        if not file_id:
            raise KeyError(f"Drive file id not known for key: {key}")

        request=self.service.files().get_media(fileId=file_id)
        target=Path(local_path)
        target.parent.mkdir(parents=True,exist_ok=True)
        with target.open("wb") as fh:
            downloader=MediaIoBaseDownload(fh,request)
            done=False
            while not done:
                _,done=downloader.next_chunk()
        return str(target)

    def delete(self,key: str) -> None:
        file_id=self._ids.get(key)
        if file_id:
            self.service.files().delete(fileId=file_id).execute()
            self._ids.pop(key,None)

    def exists(self,key: str) -> bool:
        return key in self._ids
