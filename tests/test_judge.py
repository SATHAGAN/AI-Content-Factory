from app.services.judge.mock import MockMultimodalJudge
from app.services.judge.interfaces import JudgeInput


def test_mock_judge_passes_complete_scene():
    result = MockMultimodalJudge().evaluate(
        JudgeInput(
            source_text="A fox learns to be kind.",
            narration="The fox helped a bird.",
            scene_prompt="A friendly fox helps a small bird in a sunny forest.",
            image_description="A sunny forest with a fox and bird.",
        )
    )
    assert result.passed
    assert result.score >= 0.75


def test_mock_judge_rejects_empty_narration():
    result = MockMultimodalJudge().evaluate(
        JudgeInput(
            source_text="A story.",
            narration="",
            scene_prompt="A scene.",
        )
    )
    assert not result.passed
