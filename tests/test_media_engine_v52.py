from pathlib import Path

import pytest

from app.services.media.ffmpeg import FFmpegMediaEngine
from app.services.media.models import MediaOperation, MediaOperationRequest


def test_trim_command_is_argument_safe(tmp_path):
    engine = FFmpegMediaEngine(dry_run=True)
    output = tmp_path / "out file.mp4"

    result = engine.execute(MediaOperationRequest(
        operation=MediaOperation.TRIM_VIDEO,
        input_path="input file.mp4",
        output_path=str(output),
        target_duration_seconds=8.5,
    ))

    assert result.command[0] == "ffmpeg"
    assert "input file.mp4" in result.command
    assert "-t" in result.command
    assert "8.5" in result.command
    assert result.metadata["dry_run"] is True


def test_audio_speed_chain_handles_fast_speed():
    engine = FFmpegMediaEngine(dry_run=True)
    result = engine.execute(MediaOperationRequest(
        operation=MediaOperation.ADJUST_AUDIO_SPEED,
        input_path="voice.wav",
        output_path="/tmp/voice-fast.wav",
        speed=4.0,
    ))
    command = " ".join(result.command)
    assert "atempo=2.0,atempo=2.0" in command


def test_audio_speed_rejects_invalid_value():
    engine = FFmpegMediaEngine(dry_run=True)
    with pytest.raises(ValueError):
        engine.build_command(MediaOperationRequest(
            operation=MediaOperation.ADJUST_AUDIO_SPEED,
            input_path="voice.wav",
            output_path="/tmp/out.wav",
            speed=0,
        ))


def test_merge_requires_both_inputs():
    engine = FFmpegMediaEngine(dry_run=True)
    with pytest.raises(ValueError):
        engine.build_command(MediaOperationRequest(
            operation=MediaOperation.MERGE_AUDIO_VIDEO,
            input_path="unused",
            output_path="/tmp/final.mp4",
        ))


def test_normalize_command():
    engine = FFmpegMediaEngine(dry_run=True)
    result = engine.execute(MediaOperationRequest(
        operation=MediaOperation.NORMALIZE_AUDIO,
        input_path="voice.wav",
        output_path="/tmp/normalized.wav",
    ))
    assert "loudnorm" in " ".join(result.command)


def test_extract_audio_command():
    engine = FFmpegMediaEngine(dry_run=True)
    result = engine.execute(MediaOperationRequest(
        operation=MediaOperation.EXTRACT_AUDIO,
        input_path="video.mp4",
        output_path="/tmp/audio.wav",
    ))
    command = " ".join(result.command)
    assert "-vn" in command
    assert "pcm_s16le" in command


def test_output_parent_is_created(tmp_path):
    engine = FFmpegMediaEngine(dry_run=True)
    output = tmp_path / "nested" / "folder" / "out.mp4"
    engine.build_command(MediaOperationRequest(
        operation=MediaOperation.TRIM_VIDEO,
        input_path="video.mp4",
        output_path=str(output),
        target_duration_seconds=2,
    ))
    assert output.parent.is_dir()


def test_dry_run_does_not_create_media():
    engine = FFmpegMediaEngine(dry_run=True)
    output = "/tmp/ai_factory_dry_run_should_not_exist.mp4"
    Path(output).unlink(missing_ok=True)
    engine.execute(MediaOperationRequest(
        operation=MediaOperation.TRIM_VIDEO,
        input_path="video.mp4",
        output_path=output,
        target_duration_seconds=2,
    ))
    assert not Path(output).exists()
