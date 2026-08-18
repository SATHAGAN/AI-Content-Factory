from __future__ import annotations

import time
from datetime import datetime, timezone

from app.services.pipeline.state import PipelineStage
from app.services.workers.registry import job_registry


STAGES = [
    (PipelineStage.PLANNING, 10, "Building story and scene plan"),
    (PipelineStage.GENERATING, 35, "Generating visual scenes"),
    (PipelineStage.VOICE, 50, "Generating narration"),
    (PipelineStage.RENDERING, 70, "Rendering final media"),
    (PipelineStage.MEDIA_QA, 80, "Running media quality checks"),
    (PipelineStage.AI_JUDGE, 90, "Running semantic quality judge"),
    (PipelineStage.APPROVAL, 100, "Waiting for approval"),
]


class GenerationWorker:
    """Deterministic development worker.

    Phase 13 validates orchestration and state transitions. The actual GPU
    providers are injected in later phases.
    """

    def run(self, job_id: str, delay_seconds: float = 0.0) -> dict:
        job = job_registry.get(job_id)
        if not job:
            raise KeyError(job_id)

        try:
            for stage, progress, message in STAGES:
                job_registry.update(
                    job_id,
                    status="running",
                    stage=stage.value,
                    progress=progress,
                    message=message,
                    updated_at=datetime.now(timezone.utc).isoformat(),
                )
                if delay_seconds:
                    time.sleep(delay_seconds)

            job_registry.update(
                job_id,
                status="awaiting_approval",
                stage=PipelineStage.APPROVAL.value,
                progress=100,
                message="Generation complete; awaiting approval",
                updated_at=datetime.now(timezone.utc).isoformat(),
            )
            return job_registry.get(job_id) or {}
        except Exception as exc:
            job_registry.update(
                job_id,
                status="failed",
                stage=PipelineStage.FAILED.value,
                message=str(exc),
                updated_at=datetime.now(timezone.utc).isoformat(),
            )
            raise


generation_worker = GenerationWorker()
