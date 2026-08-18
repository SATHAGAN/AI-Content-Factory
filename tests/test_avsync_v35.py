from app.services.avsync.models import check_sync
from app.services.avsync.timeline import fit_audio_to_video
from app.services.avsync.ffmpeg_plan import build_mux_plan


def test_sync_passes_within_tolerance():
    report=check_sync(5.0,5.08)
    assert report.passed
    assert report.action=="accept"


def test_sync_fails_when_difference_is_large():
    report=check_sync(5.0,5.8)
    assert not report.passed
    assert report.action=="adjust_timeline"


def test_timeline_adjustment_is_bounded():
    plan=fit_audio_to_video(6.0,5.0)
    assert 0.90 <= plan["playback_speed"] <= 1.10
    assert plan["requires_adjustment"]


def test_mux_plan_contains_video_and_audio():
    plan=build_mux_plan("video.mp4","voice.wav","final.mp4")
    assert "-map" in plan
    assert "0:v:0" in plan
    assert "1:a:0" in plan
    assert plan[-1]=="final.mp4"
