from pathlib import Path

import pytest

from app.services.subtitles.ffmpeg import SubtitleBurnInEngine
from app.services.subtitles.models import SubtitleConfig, SubtitleFormat, TranscriptWord
from app.services.subtitles.segmenter import TranscriptSegmenter
from app.services.subtitles.service import SubtitleService
from app.services.subtitles.writer import SubtitleWriter


def sample_words():
    text = [
        ("Hello", 0.0, 0.5),
        ("everyone.", 0.5, 1.2),
        ("Today", 1.4, 1.8),
        ("we", 1.8, 2.0),
        ("learn", 2.0, 2.5),
        ("something", 2.5, 3.0),
        ("new.", 3.0, 3.4),
    ]
    return [TranscriptWord(*item) for item in text]


def test_segmenter_creates_timed_segments():
    segments = TranscriptSegmenter().segment(sample_words())
    assert len(segments) >= 2
    assert segments[0].start_seconds == 0.0
    assert segments[0].end_seconds > segments[0].start_seconds
    assert segments[0].index == 1


def test_segmenter_limits_line_length():
    words = [
        TranscriptWord("verylongword", i, i + 0.2)
        for i in [0, 0.3, 0.6, 0.9, 1.2, 1.5]
    ]
    config = SubtitleConfig(max_chars_per_line=12, max_lines=2)
    segments = TranscriptSegmenter(config).segment(words)
    assert all(len(s.text.split("\n")) <= 2 for s in segments)


def test_srt_writer_format(tmp_path):
    segments = TranscriptSegmenter().segment(sample_words())
    output = tmp_path / "captions.srt"
    artifact = SubtitleWriter().write(segments, str(output), SubtitleFormat.SRT)
    content = output.read_text(encoding="utf-8")
    assert artifact.segment_count == len(segments)
    assert "1\n00:00:00,000 -->" in content
    assert "Hello" in content


def test_vtt_writer_format(tmp_path):
    segments = TranscriptSegmenter().segment(sample_words())
    output = tmp_path / "captions.vtt"
    SubtitleWriter().write(segments, str(output), SubtitleFormat.VTT)
    content = output.read_text(encoding="utf-8")
    assert content.startswith("WEBVTT")
    assert "00:00:00.000 -->" in content


def test_empty_transcript_is_supported(tmp_path):
    output = tmp_path / "empty.srt"
    artifact = SubtitleWriter().write([], str(output))
    assert artifact.segment_count == 0
    assert output.read_text(encoding="utf-8") == ""


def test_burn_in_dry_run(tmp_path):
    engine = SubtitleBurnInEngine(dry_run=True)
    output = tmp_path / "render" / "captioned.mp4"
    command = engine.execute(
        "video.mp4",
        "captions.srt",
        str(output),
    )
    joined = " ".join(command)
    assert "-vf" in command
    assert "subtitles=" in joined
    assert "libx264" in joined
    assert output.parent.is_dir()


def test_service_generates_artifact(tmp_path):
    service = SubtitleService()
    artifact = service.generate(
        sample_words(),
        str(tmp_path / "captions.srt"),
    )
    assert Path(artifact.path).is_file()
    assert artifact.segment_count > 0
