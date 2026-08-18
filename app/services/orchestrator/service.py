from __future__ import annotations

from app.services.channels.job_router import ChannelJobRouter
from app.services.channels.models import ChannelJob, Platform
from app.services.orchestrator.events import PipelineEvent
from app.services.orchestrator.models import (
    JobStatus,
    ProductionRequest,
    ProductionResult,
)


class ProductionOrchestrator:
    """Provider-neutral coordinator for the complete generation pipeline.

    Expensive providers are injected. This keeps the orchestration logic
    testable and allows individual AI models to be replaced independently.
    """

    def __init__(
        self,
        *,
        channel_router,
        content_pipeline,
        research_service,
        scene_planner,
        video_generator,
        tts_provider,
        scene_qa,
        timeline_service,
        event_sink=None,
    ):
        self.channel_router=channel_router
        self.content_pipeline=content_pipeline
        self.research_service=research_service
        self.scene_planner=scene_planner
        self.video_generator=video_generator
        self.tts_provider=tts_provider
        self.scene_qa=scene_qa
        self.timeline_service=timeline_service
        self.event_sink=event_sink or (lambda event: None)

    def _emit(self, job_id, stage, status, message, **metadata):
        self.event_sink(PipelineEvent(
            job_id=job_id,
            stage=stage,
            status=status,
            message=message,
            metadata=metadata,
        ))

    def run(self, request: ProductionRequest) -> ProductionResult:
        result=ProductionResult(
            job_id=request.job_id,
            status=JobStatus.CREATED,
            stage="created",
        )

        try:
            self._emit(request.job_id,"channel","started","Resolving channel")
            channel_job=ChannelJob(
                job_id=request.job_id,
                channel_id=request.channel_id,
                content_source_id=request.job_id,
                target_platforms=tuple(request.target_platforms),
                duration_seconds=request.target_duration_seconds,
            )
            route=self.channel_router.resolve(channel_job)

            self._emit(request.job_id,"content","started","Resolving content")
            source=self.content_pipeline.resolve(
                request.content_source
                if hasattr(request,"content_source") else None
            )

            self._emit(request.job_id,"research","started","Checking research policy")
            research=self.research_service.run(
                topic=source.content,
                category=request.category,
            )

            result.status=JobStatus.PLANNED
            result.stage="planning"
            self._emit(request.job_id,"planning","started","Creating scene plan")

            plan=self.scene_planner.plan(
                source_text=(
                    source.content
                    + (
                        "\nResearch:\n"
                        + research["packet"].summary
                        if research["required"] else ""
                    )
                ),
                category=request.category,
                language=request.language,
                target_duration_seconds=request.target_duration_seconds,
                audience=request.audience,
                tone=request.tone,
            )
            result.scene_count=len(plan.scenes)

            result.status=JobStatus.GENERATING
            result.stage="generating"
            self._emit(
                request.job_id,"generation","started",
                "Generating scene media",
                scene_count=len(plan.scenes),
            )

            # Provider contract: generate_scene(scene, channel_route) returns
            # an object containing video_path and audio_path.
            generated=[]
            for scene in plan.scenes:
                media=self.video_generator.generate_scene(
                    scene=scene,
                    channel=route["channel"],
                )
                audio=self.tts_provider.generate_scene_audio(
                    scene=scene,
                    voice=route["voice"],
                )
                generated.append((scene,media,audio))

            result.status=JobStatus.QA
            result.stage="qa"
            self._emit(request.job_id,"qa","started","Validating generated scenes")

            for scene,media,audio in generated:
                qa=self.scene_qa.validate(
                    scene=scene,
                    video=media,
                    audio=audio,
                )
                if not qa.ok:
                    raise ValueError(
                        f"Scene {scene.scene_id} failed QA: "
                        + "; ".join(qa.errors)
                    )

            result.status=JobStatus.ASSEMBLING
            result.stage="assembling"
            self._emit(request.job_id,"timeline","started","Assembling final timeline")

            clips=self.timeline_service.to_scene_clips(generated)
            assembled=self.timeline_service.merge(
                clips=clips,
                manifest_path=f"artifacts/{request.job_id}/concat.txt",
                output_path=f"artifacts/{request.job_id}/final.mp4",
            )

            result.status=JobStatus.COMPLETED
            result.stage="completed"
            result.final_video_path=assembled["output_path"]
            self._emit(
                request.job_id,"completed","success",
                "Production job completed",
                final_video_path=result.final_video_path,
            )
            return result

        except Exception as exc:
            result.status=JobStatus.FAILED
            result.errors.append(str(exc))
            self._emit(
                request.job_id,
                result.stage,
                "failed",
                str(exc),
            )
            return result
