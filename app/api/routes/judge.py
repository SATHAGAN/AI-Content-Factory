from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.deps import get_current_user
from app.models.models import User
from app.services.judge.factory import get_judge
from app.services.judge.interfaces import JudgeInput
from app.services.quality.decision import QualityGate
from app.services.safety.content_policy import BasicContentSafety

router = APIRouter(prefix="/quality", tags=["quality"])


class JudgeRequest(BaseModel):
    source_text: str = Field(min_length=1, max_length=100000)
    narration: str = Field(min_length=1, max_length=10000)
    scene_prompt: str = Field(min_length=1, max_length=10000)
    image_description: str | None = None
    media_qa_passed: bool = True


@router.post("/judge")
def judge_scene(payload: JudgeRequest, current_user: User = Depends(get_current_user)):
    safety = BasicContentSafety().check(
        "\n".join([payload.source_text, payload.narration, payload.scene_prompt])
    )

    result = get_judge().evaluate(
        JudgeInput(
            source_text=payload.source_text,
            narration=payload.narration,
            scene_prompt=payload.scene_prompt,
            image_description=payload.image_description,
        )
    )

    decision = QualityGate().decide(
        media_qa_passed=payload.media_qa_passed,
        judge_score=result.score,
        safety_passed=safety.passed,
    )

    return {
        "organization_id": current_user.organization_id,
        "judge": {
            "provider": result.provider,
            "model_id": result.model_id,
            "score": result.score,
            "passed": result.passed,
            "reasons": result.reasons,
            "warnings": result.warnings,
        },
        "safety": {
            "passed": safety.passed,
            "risk_level": safety.risk_level,
            "matched_categories": safety.matched_categories,
            "reasons": safety.reasons,
        },
        "decision": {
            "action": decision.action,
            "score": decision.score,
            "reasons": decision.reasons,
        },
    }
