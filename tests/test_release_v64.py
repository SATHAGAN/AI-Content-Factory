import json
from app.services.release import ReleaseService
def test_release_manifest(tmp_path):
    p=tmp_path/"release.json"
    m=ReleaseService().build_manifest(job_id="job",status="completed",scene_count=2,visual_count=2,
        artifacts=["a.mp4","b.mp4"],config={"platforms":["youtube","instagram"]},output_path=p)
    d=json.loads(p.read_text())
    assert d["job_id"]=="job" and d["config"]["platforms"]==["youtube","instagram"] and len(m.artifacts)==2
