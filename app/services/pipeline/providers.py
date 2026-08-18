from __future__ import annotations

from pathlib import Path

from app.services.providers.factory import get_llm_provider, get_tts_provider, get_video_provider


def run_provider_smoke_test(source_text: str, output_dir: str, duration_seconds: int, category: str):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    scenes = get_llm_provider().plan(source_text, duration_seconds, category)

    video = get_video_provider()
    tts = get_tts_provider()

    videos = [video.generate(scene, output_dir) for scene in scenes]
    audio = tts.synthesize(
        "\n".join(scene.narration for scene in scenes),
        output_dir,
    )

    return {"scenes": scenes, "videos": videos, "audio": audio}
