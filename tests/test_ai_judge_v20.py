from app.services.judge.mock_judge import MockMultimodalJudge
from app.services.judge.pipeline import AIJudgePipeline


def good_scene():
    return {
        "number":1,
        "visual_prompt":"A friendly fox walking through a sunny forest.",
        "narration":"A friendly fox walks through a sunny forest.",
    }


def test_good_scene_is_approved():
    report=MockMultimodalJudge().evaluate_scene(good_scene())
    assert report.decision=="approve"
    assert report.score>=75


def test_empty_narration_requests_regeneration():
    scene=good_scene()
    scene["narration"]=""
    report=MockMultimodalJudge().evaluate_scene(scene)
    assert report.decision=="regenerate"
    assert report.regeneration["scene_numbers"]==[1]
    assert "narration_alignment" in report.regeneration["reasons"]


def test_media_qa_failure_is_forwarded_to_judge():
    report=MockMultimodalJudge().evaluate_scene(
        good_scene(),
        media_qa={"status":"fail","issues":[{"code":"missing_audio"}]},
    )
    assert report.decision=="regenerate"
    assert report.scores["visual_quality"]==0


def test_pipeline_collects_only_failed_scenes():
    scenes=[good_scene(),{
        "number":2,
        "visual_prompt":"",
        "narration":"There is narration.",
    }]
    result=AIJudgePipeline().evaluate(scenes)
    assert result["decision"]=="regenerate"
    assert result["regeneration"]["scene_numbers"]==[2]
