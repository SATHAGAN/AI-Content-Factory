from __future__ import annotations

from app.services.production.models import ProductionJob


class ScheduledProductionRunner:
    def __init__(self, pipeline, scheduler):
        self.pipeline=pipeline
        self.scheduler=scheduler

    def run_job(self, job_record: dict):
        job=ProductionJob(
            job_id=str(job_record["job_id"]),
            channel_id=str(job_record["channel_id"]),
            content_type=str(job_record["content_type"]),
            category=str(job_record["category"]),
            language=str(job_record["language"]),
            title=str(job_record.get("title","")),
            source_text=str(job_record.get("source_text","")),
            platforms=list(job_record.get("platforms",[])),
            metadata=dict(job_record.get("metadata",{})),
        )
        return self.pipeline.run(job)
