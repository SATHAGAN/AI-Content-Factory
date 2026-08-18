from dataclasses import dataclass
from pathlib import Path

from app.services.channels.models import ChannelConfig,Platform,VoiceConfig
from app.services.channels.registry import ChannelRegistry
from app.services.channels.job_router import ChannelJobRouter
from app.services.content_source.models import ContentRequest,SourceType
from app.services.content_source.pipeline import ContentSourcePipeline
from app.services.content_source.mock_llm import MockTopicLLM
from app.services.research.mock_provider import MockResearchProvider
from app.services.research.service import ResearchService
from app.services.scene_planner.mock_llm import MockSceneLLM
from app.services.scene_planner.service import ScenePlannerService
from app.services.orchestrator.models import ProductionRequest,JobStatus
from app.services.orchestrator.service import ProductionOrchestrator
from app.services.orchestrator.adapters import QAResult
from app.services.timeline.models import SceneClip


class FakeVideo:
    def generate_scene(self, *, scene, channel):
        return type("Video",(),{
            "video_path":f"/tmp/{scene.scene_id}.mp4",
            "duration_seconds":scene.duration_seconds,
        })()


class FakeTTS:
    def generate_scene_audio(self, *, scene, voice):
        return type("Audio",(),{
            "audio_path":f"/tmp/{scene.scene_id}.wav",
            "duration_seconds":scene.duration_seconds,
        })()


class FakeQA:
    def validate(self, *, scene, video, audio):
        return QAResult(ok=True)


class FakeTimeline:
    def to_scene_clips(self, generated):
        return [
            SceneClip(
                scene_id=s.scene_id,
                video_path=v.video_path,
                duration_seconds=v.duration_seconds,
                audio_path=a.audio_path,
                metadata={"sequence":s.sequence},
            )
            for s,v,a in generated
        ]

    def merge(self, *, clips, manifest_path, output_path):
        return {"output_path":output_path}


def make_registry():
    registry=ChannelRegistry()
    registry.add(ChannelConfig(
        channel_id="facts",
        name="Facts",
        category="facts",
        language="English",
        audience="general",
        tone="educational",
        default_duration_seconds=40,
        platforms=(Platform.YOUTUBE,Platform.INSTAGRAM),
        voice=VoiceConfig(profile_id="english_narrator"),
    ))
    return registry


def test_end_to_end_orchestrator_completes():
    events=[]
    orchestrator=ProductionOrchestrator(
        channel_router=ChannelJobRouter(make_registry()),
        content_pipeline=ContentSourcePipeline(MockTopicLLM()),
        research_service=ResearchService(MockResearchProvider()),
        scene_planner=ScenePlannerService(MockSceneLLM()),
        video_generator=FakeVideo(),
        tts_provider=FakeTTS(),
        scene_qa=FakeQA(),
        timeline_service=FakeTimeline(),
        event_sink=events.append,
    )

    request=ProductionRequest(
        job_id="job-43",
        channel_id="facts",
        source_text="Why do stars shine?",
        category="facts",
        language="English",
        target_duration_seconds=40,
        audience="general",
        tone="educational",
        target_platforms=(Platform.YOUTUBE,),
    )

    # The production service accepts the source via the request compatibility
    # field used by the content pipeline.
    request.__dict__["content_source"]=ContentRequest(
        source_type=SourceType.TOPIC,
        content=request.source_text,
        category=request.category,
    )

    result=orchestrator.run(request)
    assert result.status==JobStatus.COMPLETED
    assert result.scene_count==5
    assert result.final_video_path.endswith("final.mp4")
    assert any(e.stage=="completed" for e in events)


def test_orchestrator_returns_failed_result_on_qa_failure():
    class BadQA:
        def validate(self, **kwargs):
            return QAResult(ok=False,errors=("audio/video mismatch",))

    orchestrator=ProductionOrchestrator(
        channel_router=ChannelJobRouter(make_registry()),
        content_pipeline=ContentSourcePipeline(MockTopicLLM()),
        research_service=ResearchService(MockResearchProvider()),
        scene_planner=ScenePlannerService(MockSceneLLM()),
        video_generator=FakeVideo(),
        tts_provider=FakeTTS(),
        scene_qa=BadQA(),
        timeline_service=FakeTimeline(),
    )

    request=ProductionRequest(
        job_id="job-fail",
        channel_id="facts",
        source_text="Why do stars shine?",
        category="facts",
        language="English",
        target_duration_seconds=40,
        target_platforms=(Platform.YOUTUBE,),
    )
    request.__dict__["content_source"]=ContentRequest(
        source_type=SourceType.TOPIC,
        content=request.source_text,
        category=request.category,
    )
    result=orchestrator.run(request)
    assert result.status==JobStatus.FAILED
    assert "audio/video mismatch" in result.errors[0]
