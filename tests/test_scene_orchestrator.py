from dataclasses import dataclass

from app.services.media.scene_orchestrator import SceneOrchestrator


@dataclass
class FakeVideoResult:
    provider: str = "fake-video"
    model_id: str = "fake-video-v1"
    video_path: str = "scene.mp4"
    duration_seconds: float = 5.0


class FakeVideo:
    def generate(self, request):
        assert request.frames == 80
        assert request.fps == 16
        return FakeVideoResult()


@dataclass
class FakeAudioResult:
    provider: str = "fake-tts"
    model_id: str = "fake-tts-v1"
    audio_path: str = "scene.wav"
    duration_seconds: float = 5.1


class FakeTTS:
    def synthesize(self, request):
        assert request.text == "Hello world."
        return FakeAudioResult()


def test_scene_orchestrator_generates_and_plans_sync():
    orchestrator=SceneOrchestrator(video=FakeVideo(),tts=FakeTTS())
    asset=orchestrator.generate_scene({
        "number": 1,
        "duration_seconds": 5,
        "visual_prompt": "A friendly character walking.",
        "narration": "Hello world.",
    })
    assert asset.number == 1
    assert asset.video_provider == "fake-video"
    assert asset.tts_provider == "fake-tts"
    assert asset.timing_action == "keep"
    assert asset.speed_factor == 1.0


def test_plan_generation_preserves_scene_order():
    class Video:
        def generate(self, request):
            return FakeVideoResult(duration_seconds=request.frames/request.fps)

    class TTS:
        def synthesize(self, request):
            return FakeAudioResult(duration_seconds=5.0)

    plan={
        "title":"Test",
        "target_duration_seconds":10,
        "scenes":[
            {"number":2,"duration_seconds":5,"visual_prompt":"B","narration":"B"},
            {"number":1,"duration_seconds":5,"visual_prompt":"A","narration":"A"},
        ],
    }
    result=SceneOrchestrator(video=Video(),tts=TTS()).generate_plan(plan,fps=16)
    assert result["scene_count"]==2
    assert [a["number"] for a in result["assets"]]==[1,2]
