from pathlib import Path

import pytest

from app.services.render.ffmpeg import FinalRenderEngine
from app.services.render.manifest import RenderManifestBuilder
from app.services.render.models import RenderConfig, SceneArtifact, RenderStatus
from app.services.render.service import FinalRenderService


def make_scene(tmp_path, name, order, duration):
    path = tmp_path / f"{name}.mp4"
    path.write_bytes(b"fake-video")
    return SceneArtifact(
        scene_id=name,
        video_path=str(path),
        duration_seconds=duration,
        order=order,
    )


def test_manifest_orders_scenes_and_calculates_duration(tmp_path):
    scenes = [
        make_scene(tmp_path, "scene-2", 2, 3),
        make_scene(tmp_path, "scene-1", 1, 5),
    ]
    config = RenderConfig(output_path=str(tmp_path / "final.mp4"))
    manifest = RenderManifestBuilder().build(scenes, config)

    assert [s.scene_id for s in manifest.scenes] == ["scene-1", "scene-2"]
    assert manifest.total_duration_seconds == 8
    assert manifest.metadata["scene_count"] == 2


def test_duplicate_scene_is_rejected(tmp_path):
    a = make_scene(tmp_path, "same", 1, 2)
    b = make_scene(tmp_path, "same", 2, 2)
    with pytest.raises(ValueError, match="Duplicate"):
        RenderManifestBuilder().build(
            [a, b],
            RenderConfig(output_path=str(tmp_path / "final.mp4")),
        )


def test_missing_scene_file_is_rejected(tmp_path):
    scene = SceneArtifact(
        scene_id="missing",
        video_path=str(tmp_path / "missing.mp4"),
        duration_seconds=2,
        order=1,
    )
    with pytest.raises(FileNotFoundError):
        RenderManifestBuilder().build(
            [scene],
            RenderConfig(output_path=str(tmp_path / "final.mp4")),
        )


def test_missing_music_is_rejected(tmp_path):
    scene = make_scene(tmp_path, "scene", 1, 2)
    with pytest.raises(FileNotFoundError):
        RenderManifestBuilder().build(
            [scene],
            RenderConfig(
                output_path=str(tmp_path / "final.mp4"),
                add_background_music=True,
                background_music_path=str(tmp_path / "music.mp3"),
            ),
        )


def test_dry_run_builds_concat_render_command(tmp_path):
    scene = make_scene(tmp_path, "scene", 1, 4)
    output = tmp_path / "nested" / "final.mp4"
    service = FinalRenderService(
        engine=FinalRenderEngine(dry_run=True)
    )
    result = service.render(
        [scene],
        RenderConfig(output_path=str(output)),
    )
    command = " ".join(result.command)

    assert result.status == RenderStatus.COMPLETED
    assert result.duration_seconds == 4
    assert "-f concat" in command
    assert "-movflags +faststart" in command
    assert output.parent.is_dir()
    assert not output.exists()


def test_no_scenes_rejected(tmp_path):
    with pytest.raises(ValueError):
        RenderManifestBuilder().build(
            [],
            RenderConfig(output_path=str(tmp_path / "final.mp4")),
        )


def test_subtitle_and_audio_options_are_retained_in_config(tmp_path):
    scene = make_scene(tmp_path, "scene", 1, 3)
    config = RenderConfig(
        output_path=str(tmp_path / "final.mp4"),
        add_voiceover=True,
        add_subtitles=True,
    )
    manifest = RenderManifestBuilder().build([scene], config)
    assert config.add_voiceover
    assert config.add_subtitles
    assert manifest.total_duration_seconds == 3
