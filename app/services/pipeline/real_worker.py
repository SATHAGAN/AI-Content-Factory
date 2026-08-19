from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

from app.db.session import SessionLocal
from app.models.enums import JobStatus
from app.models.models import GenerationJob, Project
from app.services.ai.mock_llm import MockLLM
from app.services.remote_gpu import RemoteGPUClient
from app.services.scene_planner.service import ScenePlannerService


ARTIFACT_ROOT = Path(os.getenv("ARTIFACT_ROOT", "artifacts/jobs"))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class RealGenerationWorker:
    """Runs the real scene-planning + GPU-video path and persists its state."""

    def _update(self, db, job: GenerationJob, *, status: JobStatus, stage: str,
                progress: int, message: str, **extra) -> None:
        output = dict(job.output_data or {})
        output.update({
            "status": status.value,
            "stage": stage,
            "progress": progress,
            "message": message,
            "updated_at": _now(),
            **extra,
        })
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

            client = RemoteGPUClient()
            settings = project.settings or {}
            source_text = settings.get("source_text", "")
            category = settings.get("category", "General")
            language = settings.get("language", "English")
            duration = float(settings.get("duration_seconds", 30))

            self._update(
                db, job, status=JobStatus.RUNNING, stage="planning",
                progress=10, message="Creating scene plan",
            )

            planner = ScenePlannerService(MockLLM())
            plan = planner.plan(
                source_text=source_text,
                category=category,
                language=language,
                target_duration_seconds=duration,
            )

            self._update(
                db, job, status=JobStatus.RUNNING, stage="video_generation",
                progress=25, message=f"Generating {len(plan.scenes)} AI video scenes",
                scene_count=len(plan.scenes),
            )

            scenes = [
                {
                    "scene_id": scene.scene_id,
                    "prompt": scene.visual_prompt,
                    "narration": scene.narration,
                    "subtitle_text": scene.subtitle_text,
                    "duration_seconds": scene.duration_seconds,
                    "width": 832,
                    "height": 480,
                    "fps": 16,
                }
                for scene in plan.scenes
            ]

            remote_result = client.generate_video(job_id=job.id, scenes=scenes)
            self._update(
                db, job, status=JobStatus.RUNNING, stage="artifact_download",
                progress=85, message="Downloading generated video",
            )

            destination = ARTIFACT_ROOT / job.id / "final.mp4"
            client.download(remote_result["output_path"], destination)

            if not destination.is_file() or destination.stat().st_size == 0:
                raise RuntimeError("GPU worker returned an empty video artifact")

            self._update(
                db, job, status=JobStatus.SUCCEEDED, stage="approval",
                progress=100, message="Generation complete; awaiting approval",
                final_video_path=str(destination),
                model_id=remote_result.get("model_id"),
                duration_seconds=remote_result.get("duration_seconds"),
            )
            return dict(job.output_data or {})
        except Exception as exc:
            job = db.query(GenerationJob).filter(GenerationJob.id == job_id).first()
            if job:
                self._update(
                    db, job, status=JobStatus.FAILED,
                    stage=(job.output_data or {}).get("stage", "failed"),
                    progress=int((job.output_data or {}).get("progress", 0)),
                    message=str(exc),
                )
            raise
        finally:
            db.close()


real_generation_worker = RealGenerationWorker()
