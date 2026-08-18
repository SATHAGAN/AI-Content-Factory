from __future__ import annotations

from app.services.recovery.models import RegenerationAttempt, RecoveryResult
from app.services.recovery.prompt_rewriter import RegenerationPromptRewriter


class SelfHealingController:
    """Bounded recovery loop for failed scenes.

    The controller never loops forever. Each failed scene gets at most
    `max_attempts` regeneration attempts before manual review.
    """

    def __init__(self, generator, evaluator, rewriter=None, max_attempts: int = 2):
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        self.generator=generator
        self.evaluator=evaluator
        self.rewriter=rewriter or RegenerationPromptRewriter()
        self.max_attempts=max_attempts

    def recover_scene(self, scene: dict, *, initial_report: dict | None = None) -> tuple[dict, list[RegenerationAttempt], bool]:
        current=dict(scene)
        attempts=[]
        report=initial_report or self.evaluator.evaluate(current)

        for attempt in range(1,self.max_attempts+1):
            if report.get("decision")=="approve":
                return current,attempts,True

            reasons=list(report.get("regeneration",{}).get("reasons",[]))
            issues=list(report.get("issues",[]))
            current["visual_prompt"]=self.rewriter.rewrite(current,reasons,issues)
            current["regeneration_attempt"]=attempt

            generated=self.generator.generate(current)
            if generated:
                current.update(generated)

            report=self.evaluator.evaluate(current)
            attempts.append(RegenerationAttempt(
                scene_number=int(current["number"]),
                attempt=attempt,
                reason=", ".join(reasons) or "quality_failure",
                prompt=current["visual_prompt"],
                status=report.get("decision","manual_review"),
            ))

            if report.get("decision")=="approve":
                return current,attempts,True

        return current,attempts,False

    def recover(self, scenes: list[dict], reports: list[dict] | None = None) -> RecoveryResult:
        reports_by_scene={
            int(r["scene_number"]):r for r in (reports or [])
            if "scene_number" in r
        }
        attempts=[]
        final=[]
        manual=[]

        for scene in sorted(scenes,key=lambda x:x["number"]):
            number=int(scene["number"])
            updated,scene_attempts,ok=self.recover_scene(
                scene,initial_report=reports_by_scene.get(number)
            )
            attempts.extend(scene_attempts)
            if ok:
                final.append(number)
            else:
                manual.append(number)

        status="completed" if not manual else ("manual_review" if final else "failed")
        return RecoveryResult(status,attempts,final,manual)
