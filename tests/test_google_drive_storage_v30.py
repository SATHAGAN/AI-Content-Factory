from pathlib import Path

from app.services.storage.google_drive import GoogleDriveStorage


def test_google_drive_adapter_uses_injected_service(tmp_path,monkeypatch):
    class Request:
        def execute(self):
            return {"id":"file-123","name":"final.mp4","size":"10","webViewLink":"https://drive.example/file"}
    class Files:
        def create(self,**kwargs):
            return Request()
        def delete(self,**kwargs):
            return Request()
    class Service:
        def files(self):
            return Files()

    # Avoid requiring the optional Google package in unit tests.
    class FakeUpload:
        def __init__(self,*args,**kwargs): pass
    import types,sys
    google=types.ModuleType("google")
    api=types.ModuleType("googleapiclient")
    http=types.ModuleType("googleapiclient.http")
    http.MediaFileUpload=FakeUpload
    sys.modules["google"]=google
    sys.modules["googleapiclient"]=api
    sys.modules["googleapiclient.http"]=http

    source=tmp_path/"final.mp4"
    source.write_bytes(b"video-data")
    store=GoogleDriveStorage(Service(),"folder-1")
    obj=store.put(str(source),"kids/job-1/final_video/final.mp4")
    assert obj.metadata["drive_file_id"]=="file-123"
    assert store.exists(obj.key)
