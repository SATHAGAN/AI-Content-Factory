from app.services.v1.environment import RuntimeEnvironment,classify_environment
from app.services.v1.profile import v1_profile_dict


def test_current_machine_without_gpu_prefers_remote():
    result=classify_environment(RuntimeEnvironment(
        name="development",
        gpu_vram_gb=None,
        inference_location="remote",
        storage_provider="google-drive",
        scheduler_enabled=False,
    ))
    assert result["local_video_possible"] is False
    assert result["recommendation"]=="remote_gpu"


def test_v1_profile_is_serializable():
    profile=v1_profile_dict()
    assert profile["llm"]["model_id"].startswith("Qwen/")
    assert profile["video"]["model_id"].startswith("Wan-AI/")
