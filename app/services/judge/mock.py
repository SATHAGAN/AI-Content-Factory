from __future__ import annotations

from app.services.judge.interfaces import JudgeInput, JudgeResult


class MockMultimodalJudge:
    """Deterministic development judge.

    It validates the judge contract without making model/network calls.
    """

    def __init__(self, pass_score: float = 0.75):
        self.pass_score = pass_score

    def evaluate(self, item: JudgeInput) -> JudgeResult:
        warnings = []
        reasons = []

        if not item.narration.strip():
            score = 0.0
            reasons.append("Narration is empty")
        elif not item.scene_prompt.strip():
            score = 0.35
            reasons.append("Scene prompt is empty")
        else:
            score = 0.92
            reasons.append("Narration and scene prompt are present")

        if item.image_description is None:
            warnings.append("No visual description supplied; visual-semantic match is limited")

        return JudgeResult(
            provider="mock",
            model_id="mock-multimodal-judge-v1",
            score=score,
            passed=score >= self.pass_score,
            reasons=reasons,
            warnings=warnings,
            raw={"mode": "deterministic"},
        )
