import json

from app.services.media.manifest import write_manifest


def test_manifest_round_trip(tmp_path):
    target=tmp_path/"manifest.json"
    path=write_manifest({"scene_count":2,"status":"ok"},str(target))
    assert json.loads(target.read_text())["scene_count"]==2
    assert path==str(target)
