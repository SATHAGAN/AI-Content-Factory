from pathlib import Path

import pytest

from app.services.caption_pipeline import CaptionPipelineService
from app.services.stt.models import STTResult, STTWord
from app.services.subtitles.models import SubtitleConfig, SubtitleFormat
from app.services.subtitles.service import SubtitleService
from app.services.subtitles.ffmpeg import SubtitleBurnInEngine


def make_stt(with_words=True):
    words = (
        STTWord("Hello", 0.0, 0.4, 0.99),
        STTWord("world.", 0.4, 0.9, 0.98),
    ) if with_words else ()
    return STTResult(
        text="Hello world.",
        language="en",
        duration_seconds=0.9,
        segments=(),
        words=words,
        provider="test",
        model="test",
    )


def test_stt_words_flow_into_srt(tmp_path):
    service = CaptionPipelineService()
    output = tmp_path / "captions.srt"

    artifact = service.generate_from_stt(make_stt(), str(output))

    assert Path(artifact.path).is_file()
    content = output.read_text(encoding="utf-8")
    assert "Hello world." in content
    assert "00:00:00,000 -->" in content


def test_stt_words_flow_into_vtt(tmp_path):
    service = CaptionPipelineService()
    output = tmp_path / "captions.vtt"

    artifact = service.generate_from_stt(
        make_stt(),
        str(output),
        SubtitleConfig(format=SubtitleFormat.VTT),
    )

    assert artifact.format == SubtitleFormat.VTT
    assert output.read_text(encoding="utf-8").startswith("WEBVTT")


def test_missing_word_timestamps_are_rejected(tmp_path):
    service = CaptionPipelineService()
    with pytest.raises(ValueError, match="no word timestamps"):
        service.generate_from_stt(
            make_stt(with_words=False),
            str(tmp_path / "captions.srt"),
        )


def test_generate_and_burn_in_uses_generated_caption_file(tmp_path):
    service = CaptionPipelineService(
        subtitle_service=SubtitleService(
            burn_in_engine=SubtitleBurnInEngine(dry_run=True)
        )
    )
    subtitle = tmp_path / "captions.srt"
    output = tmp_path / "captioned.mp4"

    artifact, command = service.generate_and_burn_in(
        make_stt(),
        "video.mp4",
        str(subtitle),
        str(output),
    )

    assert Path(artifact.path).is_file()
    assert any(str(subtitle).replace(":", "\\:") in token for token in command)
    assert str(output) in command
    assert "subtitles=" in " ".join(command)
    assert not output.exists()
