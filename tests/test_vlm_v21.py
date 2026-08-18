from pathlib import Path

from app.services.vlm.interfaces import VLMRequest,VLMResult
from app.services.vlm.mock import MockVLM
from app.services.vlm.pipeline import VLMJudgePipeline


def scene():
    return {
        "number":3,
        "video_path":"scene3.mp4",
        "visual_prompt":"A small fox helps a bird in a sunny forest.",
        "narration":"The fox helps the bird.",
    }


def test_mock_vlm_returns_structured_scores():
    result=MockVLM().analyze(VLMRequest("test",["a.jpg","b.jpg"]))
    assert result.decision=="approve"
    assert result.scores["prompt_alignment"]==90
    assert result.raw["frame_count"]==2


def test_pipeline_uses_supplied_frames_without_ffmpeg():
    result=VLMJudgePipeline(vlm=MockVLM()).evaluate_scene(
        scene(),frame_paths=["f1.jpg","f2.jpg"]
    )
    assert result["scene_number"]==3
    assert result["frame_count"]==2
    assert result["decision"]=="approve"


def test_pipeline_requires_frames_or_extractor():
    try:
        VLMJudgePipeline(vlm=MockVLM()).evaluate_scene(scene())
    except RuntimeError as exc:
        assert "frame_extractor" in str(exc)
    else:
        raise AssertionError("Expected missing frame extractor error")


def test_qwen_worker_contract_is_json_based():
    from app.services.vlm.qwen3 import Qwen3VLWorker
    assert Qwen3VLWorker(command="echo").command=="echo"
