from app.services.model_catalog.catalog import DEFAULT_V1,get_model,list_models
from app.services.model_catalog.selector import ModelSelector


def test_default_v1_profile_is_complete():
    assert DEFAULT_V1.llm.task=="llm"
    assert DEFAULT_V1.video.task=="video"
    assert DEFAULT_V1.tts.task=="tts"
    assert DEFAULT_V1.qa.task=="qa"


def test_catalog_can_filter_by_task():
    videos=list_models("video")
    assert videos
    assert all(m.task=="video" for m in videos)


def test_selector_rejects_insufficient_hardware():
    selector=ModelSelector()
    candidates=[get_model("wan2_2_ti2v_5b")]
    try:
        selector.select(candidates,gpu_vram_gb=8)
    except RuntimeError:
        pass
    else:
        raise AssertionError("Expected incompatible hardware failure")


def test_selector_accepts_lower_resource_fallback():
    selector=ModelSelector()
    result=selector.select(
        list_models("video"),
        gpu_vram_gb=8,
    )
    assert result.model_id=="Wan-AI/Wan2.1-T2V-1.3B-Diffusers"
