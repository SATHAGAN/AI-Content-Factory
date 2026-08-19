from __future__ import annotations

import math
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from app.db.session import SessionLocal
from app.models.enums import JobStatus
from app.models.models import GenerationJob, Project
from app.services.ai.factory import get_llm_provider
from app.services.scene_planner.service import ScenePlannerService

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

ARTIFACT_ROOT = Path(os.getenv("ARTIFACT_ROOT", "artifacts/jobs"))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _font(size: int):
    for candidate in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ):
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def _wrap(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textbbox((0, 0), candidate, font=font)[2] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _render_scene(scene, sequence: int, output_path: Path, width: int, height: int, fps: int) -> None:
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    width += width % 2
    height += height % 2
    proc = subprocess.Popen(
        [ffmpeg, "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{width}x{height}",
         "-r", str(fps), "-i", "-", "-an", "-c:v", "libx264", "-preset", "veryfast",
         "-pix_fmt", "yuv420p", str(output_path)],
        stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
    )
    assert proc.stdin is not None
    title_font = _font(max(32, width // 18))
    body_font = _font(max(22, width // 28))
    small_font = _font(max(16, width // 42))
    total_frames = max(1, int(scene.duration_seconds * fps))
    try:
        for frame_index in range(total_frames):
            t = frame_index / max(1, total_frames - 1)
            phase = 2 * math.pi * t
            image = Image.new("RGB", (width, height), (18, 24, 38))
            draw = ImageDraw.Draw(image)
            for y in range(height):
                ratio = y / max(1, height - 1)
                draw.line((0, y, width, y), fill=(
                    int(18 + 45 * ratio + 12 * math.sin(phase)),
                    int(24 + 55 * ratio + 10 * math.sin(phase + 1.5)),
                    int(38 + 70 * ratio + 14 * math.sin(phase + 3.0)),
                ))
            margin = int(width * 0.08)
            draw.rounded_rectangle((margin, margin, width - margin, height - margin), radius=32,
                                   fill=(10, 14, 24), outline=(220, 230, 245), width=2)
            draw.text((margin + 30, margin + 25), f"SCENE {sequence}", fill=(220, 230, 245), font=small_font)
            title_lines = _wrap(draw, scene.visual_prompt, title_font, width - 2 * (margin + 70))
            y = margin + 85
            for line in title_lines[:5]:
                draw.text((margin + 30, y), line, fill=(255, 255, 255), font=title_font)
                y += title_font.size + 12
            body_y = height - margin - 165
            narration = scene.narration or getattr(scene, "subtitle_text", "")
            for line in _wrap(draw, narration, body_font, width - 2 * (margin + 45))[:4]:
                draw.text((margin + 45, body_y), line, fill=(235, 240, 248), font=body_font)
                body_y += body_font.size + 8
            progress = int((frame_index + 1) / total_frames * (width - 2 * margin))
            draw.rounded_rectangle((margin, height - margin - 25, margin + progress, height - margin - 13),
                                   radius=6, fill=(245, 180, 70))
            draw.text((width - margin - 120, height - margin - 58), "DEMO RENDER",
                      fill=(245, 200, 120), font=small_font)
            proc.stdin.write(image.tobytes())
    finally:
        proc.stdin.close()
        stderr = proc.stderr.read().decode("utf-8", errors="replace") if proc.stderr else ""
        code = proc.wait()
        if code != 0:
            raise RuntimeError(stderr[-4000:] or "FFmpeg demo rendering failed")


class DemoGenerationWorker:
    """CPU-only renderer that validates the complete workflow without GPU cost."""

    def _update(self, db, job: GenerationJob, *, status: JobStatus, stage: str,
                progress: int, message: str, **extra) -> None:
        output = dict(job.output_data or {})
        output.update({"status": status.value, "stage": stage, "progress": progress,
                       "message": message, "updated_at": _now(), **extra})
        job.status = status
        job.output_data = output
        db.commit()
        db.refresh(job)

    def run(self, job_id: str) -> dict:
        db = SessionLocal()
        try:
            job = db.query(GenerationJob).filter(GenerationJob.id == job_id).first()
            if not job:
                raise KeyError(job_id)
            project = db.query(Project).filter(Project.id == job.project_id).first()
            if not project:
                raise KeyError(f"project:{job.project_id}")
            settings = project.settings or {}
            duration = float(settings.get("duration_seconds", 30))
            llm_provider = os.getenv("LLM_PROVIDER", "mock")
            self._update(db, job, status=JobStatus.RUNNING, stage="planning", progress=10,
                         message="Creating scene plan")
            llm = get_llm_provider(provider=llm_provider, base_url=os.getenv("LLM_BASE_URL"),
                                   model_id=os.getenv("LLM_MODEL_ID"), api_key=os.getenv("LLM_API_KEY"))
            plan = ScenePlannerService(llm).plan(
                source_text=settings.get("source_text", ""), category=settings.get("category", "General"),
                language=settings.get("language", "English"), target_duration_seconds=duration,
                scene_duration_seconds=8.0)
            job_dir = ARTIFACT_ROOT / job.id
            job_dir.mkdir(parents=True, exist_ok=True)
            self._update(db, job, status=JobStatus.RUNNING, stage="demo_video_render", progress=35,
                         message=f"Rendering {len(plan.scenes)} demo scenes", scene_count=len(plan.scenes),
                         llm_provider=llm_provider)
            clips: list[Path] = []
            total_duration = 0.0
            for sequence, scene in enumerate(plan.scenes, 1):
                clip = job_dir / f"{scene.scene_id}.mp4"
                _render_scene(scene, sequence, clip, width=832, height=480, fps=16)
                clips.append(clip)
                total_duration += float(scene.duration_seconds)
            concat_file = job_dir / "concat.txt"
            concat_file.write_text("\n".join(f"file '{p.resolve().as_posix()}'" for p in clips) + "\n", encoding="utf-8")
            final_path = job_dir / "final.mp4"
            ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
            subprocess.run([ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file),
                            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-movflags", "+faststart",
                            str(final_path)], check=True, capture_output=True, text=True)
            if not final_path.is_file() or final_path.stat().st_size == 0:
                raise RuntimeError("Demo renderer produced an empty video artifact")
            self._update(db, job, status=JobStatus.SUCCEEDED, stage="approval", progress=100,
                         message="Demo video ready; awaiting approval", final_video_path=str(final_path),
                         model_id="demo-render-v1", duration_seconds=total_duration,
                         scene_count=len(plan.scenes), demo=True,
                         quality_note="CPU demo render validates workflow and media delivery; it is not AI-generated visual content.")
            output = dict(job.output_data or {})
            output["status"] = "awaiting_approval"
            job.output_data = output
            db.commit()
            db.refresh(job)
            return dict(job.output_data or {})
        except Exception as exc:
            job = db.query(GenerationJob).filter(GenerationJob.id == job_id).first()
            if job:
                self._update(db, job, status=JobStatus.FAILED,
                             stage=(job.output_data or {}).get("stage", "failed"),
                             progress=int((job.output_data or {}).get("progress", 0)), message=str(exc))
            raise
        finally:
            db.close()


demo_generation_worker = DemoGenerationWorker()
