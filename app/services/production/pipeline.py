from __future__ import annotations

from app.services.production.models import ProductionJob, ProductionResult
from app.services.production.state import ProductionStateStore


class ProductionPipeline:
    """Orchestrates the complete production lifecycle.

    Concrete services are injected so every provider remains replaceable.
    """

    def __init__(
        self,
        *,
        planner,
        media_generator,
        qa,
        finalizer,
        publisher,
        state_store=None,
    ):
        self.planner=planner
        self.media_generator=media_generator
        self.qa=qa
        self.finalizer=finalizer
        self.publisher=publisher
        self.state=state_store or ProductionStateStore()

    def run(self, job: ProductionJob) -> ProductionResult:
        result=ProductionResult(job.job_id,"running")
        try:
            self.state.transition(job.job_id,status="running",stage="planning")
            plan=self.planner.plan(
                job.source_text,
                category=job.category,
                language=job.language,
                duration_seconds=job.metadata.get("duration_seconds",60),
                tone=job.metadata.get("tone","engaging"),
                audience=job.metadata.get("audience","general"),
            )
            result.stages.append("planning")

            self.state.transition(job.job_id,status="running",stage="media_generation")
            scenes=self.media_generator.generate(plan,job)
            result.outputs["scenes"]=scenes
            result.stages.append("media_generation")

            self.state.transition(job.job_id,status="running",stage="quality_assurance")
            qa_result=self.qa.evaluate(plan,scenes,job)
            result.outputs["qa"]=qa_result
            result.stages.append("quality_assurance")

            if not qa_result.get("passed",False):
                raise RuntimeError("Production QA rejected the generated content")

            self.state.transition(job.job_id,status="running",stage="finalization")
            final=self.finalizer.render(plan,scenes,job)
            result.outputs["final"]=final
            result.stages.append("finalization")

            self.state.transition(job.job_id,status="running",stage="publishing")
            published=self.publisher.publish(final,job)
            result.outputs["published"]=published
            result.stages.append("publishing")

            self.state.transition(job.job_id,status="completed",stage="completed")
            result.status="completed"
            return result

        except Exception as exc:
            self.state.transition(
                job.job_id,
                status="failed",
                stage=self.state.get(job.job_id).stage,
                error=str(exc),
            )
            result.status="failed"
            result.errors.append(str(exc))
            return result
