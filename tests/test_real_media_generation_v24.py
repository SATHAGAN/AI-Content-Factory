from pathlib import Path

from app.services.media.generation import RealMediaGenerationService


class FakeVideo:
    def generate(self, request, output_path):
        Path(output_path).write_bytes(b"video")
        return {
            "video_path":output_path,
            "duration_seconds":5.0,
            "provider":"fake-video",
            "model_id":"fake-v1",
        }


class FakeTTS:
    def synthesize(self, request, output_path):
        Path(output_path).write_bytes(b"audio")
        return {
            "audio_path":output_path,
            "duration_seconds":5.0,
            "provider":"fake-tts",
            "model_id":"fake-tts-v1",
        }


def test_generation_service_produces_both_assets(tmp_path):
    service=RealMediaGenerationService(video=FakeVideo(),tts=FakeTTS())
    result=service.generate_scene({
        "number":2,
        "duration_seconds":5,
        "visual_prompt":"A fox walks through a forest.",
        "narration":"The fox walks.",
    },str(tmp_path))
    assert Path(result["video_path"]).exists()
    assert Path(result["audio_path"]).exists()
    assert result["video_provider"]=="fake-video"
    assert result["tts_provider"]=="fake-tts"


def test_local_provider_is_lazy():
    from app.services.media.providers.huggingface_diffusers import DiffusersVideoProvider
    provider=DiffusersVideoProvider("test-model")
    assert provider.model_id=="test-model"
