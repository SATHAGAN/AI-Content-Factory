from app.services.quality.media_qa import MediaQualityAssurance
from app.services.quality.models import MediaProbe
from app.services.quality.regeneration import regeneration_plan


def test_good_scene_passes():
    qa=MediaQualityAssurance()
    report=qa.evaluate([(1,MediaProbe(
        path="x.mp4",duration_seconds=10,width=1080,height=1920,
        fps=30,has_video=True,has_audio=True
    ),10)])
    assert report.status=="pass"
    assert report.score==100


def test_missing_audio_fails_and_requests_scene_regeneration():
    qa=MediaQualityAssurance()
    report=qa.evaluate([(3,MediaProbe(
        path="x.mp4",duration_seconds=10,width=1080,height=1920,
        fps=30,has_video=True,has_audio=False
    ),10)])
    assert report.status=="fail"
    plan=regeneration_plan(report)
    assert plan["required"] is True
    assert plan["scene_numbers"]==[3]
    assert "missing_audio" in plan["reason_codes"]


def test_duration_drift_fails():
    qa=MediaQualityAssurance(duration_tolerance=.1)
    report=qa.evaluate([(1,MediaProbe(
        path="x.mp4",duration_seconds=15,width=1080,height=1920,
        fps=30,has_video=True,has_audio=True
    ),10)])
    assert report.status=="fail"
    assert any(x.code=="duration_mismatch" for x in report.issues)


def test_low_resolution_is_review_not_hard_fail():
    qa=MediaQualityAssurance()
    report=qa.evaluate([(1,MediaProbe(
        path="x.mp4",duration_seconds=10,width=240,height=320,
        fps=30,has_video=True,has_audio=True
    ),10)])
    assert report.status=="review"
