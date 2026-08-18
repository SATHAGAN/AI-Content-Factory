from pathlib import Path

from app.services.presentation.subtitle_builder import SubtitleBuilder
from app.services.presentation.platform_formats import get_platform_format
from app.services.presentation.thumbnail import ThumbnailPlanBuilder


def test_subtitles_are_continuous_and_valid_srt():
    scenes=[
        {"number":2,"video_duration_seconds":5,"narration":"Second"},
        {"number":1,"video_duration_seconds":3,"narration":"First"},
    ]
    builder=SubtitleBuilder()
    cues=builder.build(scenes)
    assert cues[0].start_seconds==0
    assert cues[0].end_seconds==3
    assert cues[1].start_seconds==3
    srt=builder.to_srt(cues)
    assert "00:00:00,000 --> 00:00:03,000" in srt
    assert "First" in srt


def test_platform_formats_are_dynamic():
    assert get_platform_format("youtube_long").aspect_ratio=="16:9"
    assert get_platform_format("youtube_short").width==1080
    assert get_platform_format("instagram_reel").height==1920


def test_thumbnail_plan_uses_content_plan():
    plan=ThumbnailPlanBuilder().build({
        "title":"Amazing Fox Story",
        "hook":"A surprising forest adventure!"
    })
    assert plan["headline"]=="Amazing Fox Story"
    assert "forest" in plan["generation_prompt"]
