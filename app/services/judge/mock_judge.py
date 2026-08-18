from __future__ import annotations
from app.services.judge.models import DEFAULT_CRITERIA, JudgeIssue, JudgeReport
from app.services.judge.interfaces import JudgeInput, JudgeResult


class MockMultimodalJudge:
    """Deterministic judge used until a real multimodal model is connected."""

    provider="mock"
    model_id="mock-multimodal-judge-v1"

    def evaluate_scene(
        self,
        scene: dict,
        *,
        media_qa: dict | None = None,
        safety: dict | None = None,
    ) -> JudgeReport:
        issues=[]
        scores={c.name: 100.0 for c in DEFAULT_CRITERIA}

        if media_qa:
            if media_qa.get("status") == "fail":
                scores["visual_quality"]=0.0
                issues.append(JudgeIssue(
                    "visual_quality","error","Media QA failed",
                    evidence=str(media_qa.get("issues",[])),
                    scene_number=scene.get("number"),
                ))
            elif media_qa.get("status") == "review":
                scores["visual_quality"]=70.0

        if safety and not safety.get("passed", True):
            scores["content_safety"]=0.0
            issues.append(JudgeIssue(
                "content_safety","error","Safety gate did not pass",
                evidence=str(safety.get("matched_categories",[])),
                scene_number=scene.get("number"),
            ))

        # Deterministic structural checks stand in for semantic model scoring.
        if not scene.get("visual_prompt"):
            scores["prompt_alignment"]=0.0
            issues.append(JudgeIssue(
                "prompt_alignment","error","Visual prompt is empty",
                scene_number=scene.get("number"),
            ))
        if not scene.get("narration"):
            scores["narration_alignment"]=0.0
            issues.append(JudgeIssue(
                "narration_alignment","error","Narration is empty",
                scene_number=scene.get("number"),
            ))

        weighted=sum(scores[c.name]*c.weight for c in DEFAULT_CRITERIA)
        threshold=75.0
        decision="approve" if weighted >= threshold and not any(i.severity=="error" for i in issues) else "regenerate"
        regeneration={
            "required":decision=="regenerate",
            "scene_numbers":[scene.get("number")] if decision=="regenerate" else [],
            "reasons":sorted({i.criterion for i in issues}),
        }
        return JudgeReport(decision,weighted,threshold,issues,scores,regeneration)

    def evaluate(self, item: JudgeInput) -> JudgeResult:
        scene = {
            "number": 1,
            "visual_prompt": item.scene_prompt,
            "narration": item.narration,
        }
        report = self.evaluate_scene(scene)
        return JudgeResult(
            provider=self.provider,
            model_id=self.model_id,
            score=report.score,
            passed=report.decision == "approve",
            reasons=[i.message for i in report.issues],
            warnings=[i.message for i in report.issues if i.severity == "warning"],
            raw=report.to_dict(),
        )
