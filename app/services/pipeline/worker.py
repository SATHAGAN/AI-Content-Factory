from __future__ import annotations

from datetime import datetime, timezone

from app.db.session import SessionLocal
from app.models.enums import JobStatus
from app.models.models import GenerationJob
from app.services.pipeline.state import PipelineStage


STAGES = [
    (PipelineStage.PLANNING, 10, "Building story and scene plan"),
    (PipelineStage.GENERATING, 35, "Generating visual scenes"),
    (PipelineStage.VOICE, 50, "Generating narration"),
    (PipelineStage.RENDERING, 70, "Rendering final media"),
    (PipelineStage.MEDIA_QA, 80, "Running media quality checks"),
    (PipelineStage.AI_JUDGE, 90, "Running semantic quality judge"),
    (PipelineStage.APPROVAL, 100, "Waiting for approval"),
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class GenerationWorker:
    """Development worker with durable PostgreSQL job state.

    This worker intentionally keeps the deterministic development stages until
    the real GPU-backed production orchestrator is enabled. Unlike the former
    in-process registry, every transition is now persisted in GenerationJob.
    """

    def _update(self, db, job: GenerationJob, *, status: JobStatus, stage: str,
                progress: int, message: str) -> None:
        output = dict(job.output_data or {})
        output.update({
            "status": status.value,
            "stage": stage,
            "progress": progress,
            "message": message,
            "updated_at": _now(),
        })
        job.status = status
        job.output_data = output
        db.commit()
        db.refresh(job)

    def run(self, job_id: str, delay_seconds: float = 0.0) -> dict:
        del delay_seconds  # kept for backwards-compatible call signatures

        db = SessionLocal()
        try:
            job = db.query(GenerationJob).filter(GenerationJob.id == job_id).first()
            if not job:
                raise KeyError(job_id)

            for stage, progress, message in STAGES:
                self._update(
                    db,
                    job,
                    status=JobStatus.RUNNING,
                    stage=stage.value,
                    progress=progress,
                    message=message,
                )

            self._update(
                db,
                job,
                status=JobStatus.SUCCEEDED,
                stage=PipelineStage.APPROVAL.value,
                progress=100,
                message="Generation complete; awaiting approval",
            )
            return dict(job.output_data or {})
        except Exception as exc:
            job = db.query(GenerationJob).filter(GenerationJob.id == job_id).first()
            if job:
                self._update(
                    db,
                    job,
                    status=JobStatus.FAILED,
                    stage=PipelineStage.FAILED.value,
                    progress=int((job.output_data or {}).get("progress", 0)),
                    message=str(exc),
                )
            raise
        finally:
            db.close()


generation_worker = GenerationWorker()
