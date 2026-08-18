import pytest


def test_wan_provider_fails_actionably_without_cuda(monkeypatch):
    monkeypatch.setenv("VIDEO_PROVIDER", "wan")
    monkeypatch.setenv("VIDEO_DEVICE", "cuda")

    from app.services.providers.factory import get_video_provider
    provider = get_video_provider()

    try:
        import torch
        if torch.cuda.is_available():
            pytest.skip("CUDA available in this environment")
    except ImportError:
        pass

    with pytest.raises(RuntimeError, match="CUDA|torch and diffusers"):
        provider.generate(
            type("Scene", (), {
                "scene_id": "s1",
                "prompt": "A fox in a forest",
                "negative_prompt": "",
                "duration_seconds": 5,
            })(),
            "/tmp/acf-phase14",
        )
