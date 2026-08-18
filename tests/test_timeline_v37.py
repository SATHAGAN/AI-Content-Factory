from pathlib import Path

from app.services.timeline.models import SceneClip
from app.services.timeline.builder import TimelineBuilder
from app.services.timeline.validator import validate_timeline
from app.services.timeline.splitter import split_duration


def clip(tmp_path,name,seq,duration=5):
    p=tmp_path/name
    p.write_bytes(b"video")
    return SceneClip(
        scene_id=name,
        video_path=str(p),
        duration_seconds=duration,
        metadata={"sequence":seq},
    )


def test_timeline_orders_clips_and_sums_duration(tmp_path):
    clips=[
        clip(tmp_path,"scene2.mp4",2,4),
        clip(tmp_path,"scene1.mp4",1,5),
    ]
    timeline=TimelineBuilder().build(clips)
    assert [c.scene_id for c in timeline.clips]==["scene1.mp4","scene2.mp4"]
    assert timeline.total_duration_seconds==9


def test_timeline_rejects_duplicate_scene_ids(tmp_path):
    a=clip(tmp_path,"scene.mp4",1)
    b=clip(tmp_path,"scene.mp4",2)
    timeline=TimelineBuilder().build([a,b])
    assert any("Duplicate" in e for e in validate_timeline(timeline))


def test_timeline_can_limit_to_ten_minutes(tmp_path):
    clips=[clip(tmp_path,f"s{i}.mp4",i,60) for i in range(10)]
    timeline=TimelineBuilder().build(clips)
    assert validate_timeline(timeline,max_duration_seconds=600)==[]


def test_split_duration_for_long_form():
    parts=split_duration(605,8)
    assert len(parts)==76
    assert abs(sum(parts)-605)<1e-9
    assert parts[-1]==5


def test_split_duration_rejects_invalid_input():
    import pytest
    with pytest.raises(ValueError):
        split_duration(0,8)
