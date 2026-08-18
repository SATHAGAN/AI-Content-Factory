from app.services.providers.factory import get_llm_provider, get_tts_provider, get_video_provider


def test_default_providers_are_safe_for_cpu_environment():
    llm = get_llm_provider()
    video = get_video_provider()
    tts = get_tts_provider()

    assert llm is not None
    assert video.provider == "mock"
    assert tts.provider == "mock"


def test_mock_provider_pipeline(tmp_path):
    from app.services.pipeline.providers import run_provider_smoke_test

    result = run_provider_smoke_test(
        "A friendly fox helps a bird.",
        str(tmp_path),
        60,
        "Kids",
    )
    assert len(result["scenes"]) >= 1
    assert result["videos"][0].uri.endswith(".mp4")
    assert result["audio"].uri.endswith(".wav")
