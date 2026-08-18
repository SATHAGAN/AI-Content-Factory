from pathlib import Path

import pytest

from app.services.audio_mix.ffmpeg import AudioMixEngine
from app.services.audio_mix.models import AudioMixConfig, AudioMixRequest


def test_voice_only_mix(tmp_path):
    engine = AudioMixEngine(dry_run=True)
    result = engine.execute(AudioMixRequest(
        video_path="video.mp4",
        voice_path="voice.wav",
        music_path=None,
        output_path=str(tmp_path / "out.mp4"),
    ))
    command = " ".join(result.command)
    assert result.voice_enabled
    assert not result.music_enabled
    assert "loudnorm=I=-16" in command
    assert "-map 0:v:0" in command


def test_voice_priority_ducks_music(tmp_path):
    engine = AudioMixEngine(dry_run=True)
    result = engine.execute(AudioMixRequest(
        video_path="video.mp4",
        voice_path="voice.wav",
        music_path="music.mp3",
        output_path=str(tmp_path / "out.mp4"),
        config=AudioMixConfig(
            voice_volume=1.0,
            music_volume=0.2,
            ducked_music_volume=0.05,
            music_ducking=True,
        ),
    ))
    command = " ".join(result.command)
    assert "volume=0.0500" in command
    assert "amix=inputs=2" in command


def test_music_without_voice_uses_normal_music_volume(tmp_path):
    engine = AudioMixEngine(dry_run=True)
    result = engine.execute(AudioMixRequest(
        video_path="video.mp4",
        voice_path=None,
        music_path="music.mp3",
        output_path=str(tmp_path / "out.mp4"),
        config=AudioMixConfig(music_volume=0.25),
    ))
    command = " ".join(result.command)
    assert "volume=0.2500" in command


def test_invalid_volume_rejected(tmp_path):
    engine = AudioMixEngine(dry_run=True)
    with pytest.raises(ValueError):
        engine.build_command(AudioMixRequest(
            video_path="video.mp4",
            voice_path="voice.wav",
            music_path=None,
            output_path=str(tmp_path / "out.mp4"),
            config=AudioMixConfig(voice_volume=5),
        ))


def test_at_least_one_audio_source_required(tmp_path):
    engine = AudioMixEngine(dry_run=True)
    with pytest.raises(ValueError):
        engine.build_command(AudioMixRequest(
            video_path="video.mp4",
            voice_path=None,
            music_path=None,
            output_path=str(tmp_path / "out.mp4"),
        ))


def test_real_file_validation(tmp_path):
    engine = AudioMixEngine(dry_run=False)
    video = tmp_path / "video.mp4"
    voice = tmp_path / "voice.wav"
    video.write_bytes(b"video")
    voice.write_bytes(b"audio")
    request = AudioMixRequest(
        video_path=str(video),
        voice_path=str(voice),
        music_path=None,
        output_path=str(tmp_path / "nested" / "out.mp4"),
    )
    command = engine.build_command(request)
    assert Path(request.output_path).parent.is_dir()
    assert str(video) in command
    assert str(voice) in command
