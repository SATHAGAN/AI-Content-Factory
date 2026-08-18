from app.services.rendering.audio_timeline import AudioTimelineBuilder


def test_timeline_orders_scenes_and_accumulates_time():
    timeline=AudioTimelineBuilder().build([
        {"number":2,"video_duration_seconds":5,"audio_duration_seconds":5,"audio_path":"b.wav"},
        {"number":1,"video_duration_seconds":4,"audio_duration_seconds":4,"audio_path":"a.wav"},
    ])
    assert [s.scene_number for s in timeline.segments]==[1,2]
    assert timeline.segments[0].start_seconds==0
    assert timeline.segments[1].start_seconds==4
    assert timeline.duration_seconds==9


def test_small_audio_mismatch_is_time_stretched():
    timeline=AudioTimelineBuilder().build([
        {"number":1,"video_duration_seconds":10,"audio_duration_seconds":11,"audio_path":"a.wav"},
    ])
    assert timeline.segments[0].action=="time_stretch"
    assert timeline.segments[0].speed_factor==1.1


def test_large_mismatch_requires_review():
    timeline=AudioTimelineBuilder().build([
        {"number":1,"video_duration_seconds":10,"audio_duration_seconds":30,"audio_path":"a.wav"},
    ])
    assert timeline.segments[0].action=="regenerate_or_recut"


def test_missing_audio_is_not_invented():
    timeline=AudioTimelineBuilder().build([
        {"number":1,"video_duration_seconds":10,"audio_duration_seconds":0,"audio_path":None},
    ])
    assert timeline.segments==[]
