from __future__ import annotations

import gc
import os
import secrets
import subprocess
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

app = FastAPI(title="AI Content Factory GPU Worker", version="1.0.0")

MODEL_ID = os.getenv("VIDEO_MODEL_ID", "Wan-AI/Wan2.1-T2V-1.3B-Diffusers")
DEVICE = os.getenv("VIDEO_DEVICE", "cuda")
WORK_ROOT = Path(os.getenv("WORK_ROOT", "/workspace/ai-content-factory"))
WORKER_TOKEN = os.getenv("GPU_WORKER_TOKEN", "")
ENABLE_TTS = os.getenv("ENABLE_TTS", "true").lower() == "true"
TTS_MODEL_ID = os.getenv("TTS_MODEL_ID", "Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice")


class SceneInput(BaseModel):
    scene_id: str = Field(min_length=1, max_length=100)
    prompt: str = Field(min_length=1, max_length=10000)
    narration: str = ""
    subtitle_text: str = ""
    duration_seconds: float = Field(default=8.0, ge=2.0, le=30.0)
    width: int = Field(default=832, ge=256, le=1920)
    height: int = Field(default=480, ge=256, le=1920)
    fps: int = Field(default=16, ge=8, le=30)
    seed: int | None = None


class VideoRequest(BaseModel):
    job_id: str = Field(min_length=1, max_length=100)
    scenes: list[SceneInput] = Field(min_length=1, max_length=20)


def _authorized(token: str | None) -> bool:
    if not WORKER_TOKEN:
        return False
    return bool(token) and secrets.compare_digest(token, WORKER_TOKEN)


def _require_auth(token: str | None) -> None:
    if not _authorized(token):
        raise HTTPException(status_code=401, detail="Invalid GPU worker token")


def _ffmpeg(*args: str) -> None:
    result = subprocess.run(
        ["ffmpeg", "-y", *args],
        capture_output=True,
        text=True,
        timeout=1800,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr[-5000:])


def _load_video_pipeline():
    import torch
    from diffusers import WanPipeline

    if DEVICE.startswith("cuda") and not torch.cuda.is_available():
        raise RuntimeError("CUDA is unavailable on the GPU worker")

    pipe = WanPipeline.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.bfloat16 if DEVICE.startswith("cuda") else torch.float32,
    )
    pipe.to(DEVICE)
    return pipe


def _generate_scene(pipe, scene: SceneInput, output_path: Path) -> None:
    import torch
    from diffusers.utils import export_to_video

    frames = max(17, int(scene.duration_seconds * scene.fps) + 1)
    kwargs = {
        "prompt": scene.prompt,
        "negative_prompt": "blurry, distorted, low quality, watermark, text artifacts",
        "height": scene.height,
        "width": scene.width,
        "num_frames": frames,
    }
    if scene.seed is not None:
        kwargs["generator"] = torch.Generator(device=DEVICE).manual_seed(scene.seed)

    with torch.inference_mode():
        result = pipe(**kwargs)
    export_to_video(result.frames[0], str(output_path), fps=scene.fps)


def _add_tts(video_path: Path, narration: str, output_path: Path, tts_model) -> None:
    if not narration.strip():
        output_path.write_bytes(video_path.read_bytes())
        return

    import soundfile as sf

    wavs, sample_rate = tts_model.generate_custom_voice(
        text=narration,
        language="English",
        speaker=os.getenv("TTS_SPEAKER", "Ryan"),
        instruct="Speak naturally and clearly for short-form educational video narration.",
    )
    audio_path = output_path.with_suffix(".wav")
    sf.write(str(audio_path), wavs[0], sample_rate)
    _ffmpeg(
        "-i", str(video_path),
        "-i", str(audio_path),
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        str(output_path),
    )
    audio_path.unlink(missing_ok=True)


def _write_srt(scenes: list[SceneInput], path: Path) -> None:
    def timestamp(seconds: float) -> str:
        total_ms = int(round(seconds * 1000))
        hours, rem = divmod(total_ms, 3_600_000)
        minutes, rem = divmod(rem, 60_000)
        secs, millis = divmod(rem, 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    current = 0.0
    lines: list[str] = []
    for index, scene in enumerate(scenes, 1):
        text = scene.subtitle_text.strip() or scene.narration.strip()
        if text:
            lines.extend([
                str(index),
                f"{timestamp(current)} --> {timestamp(current + scene.duration_seconds)}",
                text,
                "",
            ])
        current += scene.duration_seconds
    path.write_text("\n".join(lines), encoding="utf-8")


@app.get("/health")
def health():
    try:
        import torch
        return {
            "status": "ok",
            "cuda_available": torch.cuda.is_available(),
            "gpu_count": torch.cuda.device_count(),
            "model_id": MODEL_ID,
            "tts_enabled": ENABLE_TTS,
        }
    except Exception as exc:
        return {"status": "degraded", "error": str(exc), "model_id": MODEL_ID}


@app.post("/generate-video")
def generate_video(request: VideoRequest, x_worker_token: str | None = Header(default=None)):
    _require_auth(x_worker_token)

    job_dir = WORK_ROOT / request.job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    try:
        pipe = _load_video_pipeline()
        clips: list[Path] = []
        for scene in request.scenes:
            raw_path = job_dir / f"{scene.scene_id}_raw.mp4"
            _generate_scene(pipe, scene, raw_path)
            clips.append(raw_path)

        if ENABLE_TTS:
            del pipe
            gc.collect()
            try:
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            except Exception:
                pass

        if ENABLE_TTS:
            try:
                import torch
                from qwen_tts import Qwen3TTSModel

                tts_model = Qwen3TTSModel.from_pretrained(
                    TTS_MODEL_ID,
                    device_map=DEVICE,
                    dtype=torch.bfloat16 if DEVICE.startswith("cuda") else torch.float32,
                )
            except Exception as exc:
                raise RuntimeError(f"TTS initialization failed: {exc}") from exc

            voiced: list[Path] = []
            for scene, raw_path in zip(request.scenes, clips):
                voiced_path = job_dir / f"{scene.scene_id}_voiced.mp4"
                _add_tts(raw_path, scene.narration, voiced_path, tts_model)
                voiced.append(voiced_path)
            clips = voiced

        concat_file = job_dir / "concat.txt"
        concat_file.write_text(
            "\n".join(f"file '{path.as_posix()}'" for path in clips) + "\n",
            encoding="utf-8",
        )
        assembled = job_dir / "assembled.mp4"
        _ffmpeg("-f", "concat", "-safe", "0", "-i", str(concat_file), "-c", "copy", str(assembled))

        srt_path = job_dir / "subtitles.srt"
        _write_srt(request.scenes, srt_path)
        final_path = job_dir / "final.mp4"
        if srt_path.read_text(encoding="utf-8").strip():
            _ffmpeg(
                "-i", str(assembled),
                "-vf", f"subtitles={srt_path.as_posix()}",
                "-c:v", "libx264",
                "-preset", "veryfast",
                "-crf", "20",
                "-c:a", "aac",
                "-movflags", "+faststart",
                str(final_path),
            )
        else:
            final_path.write_bytes(assembled.read_bytes())

        return {
            "status": "succeeded",
            "model_id": MODEL_ID,
            "output_path": str(final_path),
            "duration_seconds": sum(scene.duration_seconds for scene in request.scenes),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/download")
def download(path: str = Query(min_length=1), x_worker_token: str | None = Header(default=None)):
    _require_auth(x_worker_token)
    requested = Path(path).resolve()
    root = WORK_ROOT.resolve()
    if root not in requested.parents or not requested.is_file():
        raise HTTPException(status_code=404, detail="Artifact not found")
    return FileResponse(requested, media_type="video/mp4", filename=requested.name)
