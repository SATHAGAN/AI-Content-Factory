from pathlib import Path

from app.services.storage.local import LocalObjectStorage
from app.services.storage.lifecycle import AssetKeyBuilder,AssetLifecycle


def test_local_storage_round_trip(tmp_path):
    source=tmp_path/"source.mp4"
    source.write_bytes(b"video-data")
    store=LocalObjectStorage(str(tmp_path/"store"))
    obj=store.put(str(source),"kids/job-1/final_video/final.mp4")
    assert obj.size_bytes==10
    assert store.exists(obj.key)
    target=tmp_path/"download.mp4"
    store.get(obj.key,str(target))
    assert target.read_bytes()==b"video-data"
    store.delete(obj.key)
    assert not store.exists(obj.key)


def test_storage_key_is_safe_and_deterministic():
    key=AssetKeyBuilder().build("kids channel","job/1","final_video","final.mp4")
    assert key=="kids_channel/job_1/final_video/final.mp4"


def test_asset_lifecycle():
    lifecycle=AssetLifecycle()
    assert lifecycle.retention_class("final_video")=="permanent"
    assert lifecycle.retention_class("scene_video")=="temporary"
