import os


def test_scene_generation_worker_with_mock_providers(monkeypatch, tmp_path):
    monkeypatch.setenv("VIDEO_PROVIDER", "mock")
    monkeypatch.setenv("TTS_PROVIDER", "mock")
    monkeypatch.chdir(tmp_path)

    from app.services.workers.generate_scene import generate_scene

    result = generate_scene({
        "scene": {
            "number": 1,
            "visual_prompt": "A friendly animated fox walking through a forest",
            "narration": "The fox began a new adventure.",
        },
        "language": "en",
        "voice": "default",
        "width": 480,
        "height": 832,
        "frames": 32,
        "fps": 16,
    })

    assert result["status"] == "generated"
    assert result["video_provider"] == "mock"
    assert result["tts_provider"] == "mock"
    assert os.path.exists(result["video_path"])
    assert os.path.exists(result["audio_path"])
