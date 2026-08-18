from app.services.visual_qa import VisualQAService
def test_missing_asset_fails():
    r=VisualQAService().inspect("missing.mp4",expected_duration=5,prompt="x")
    assert not r.passed and r.retry_recommended
def test_good_asset_passes(tmp_path):
    p=tmp_path/"v.mp4";p.write_bytes(b"x")
    r=VisualQAService().inspect(str(p),expected_duration=5,actual_duration=5.1,prompt="clear subject")
    assert r.passed
def test_duration_drift_fails(tmp_path):
    p=tmp_path/"v.mp4";p.write_bytes(b"x")
    r=VisualQAService().inspect(str(p),expected_duration=5,actual_duration=7,prompt="clear subject")
    assert not r.passed
