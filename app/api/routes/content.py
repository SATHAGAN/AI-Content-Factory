import os

from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import get_current_user
from app.models.models import User
from app.schemas.content import ContentPlanResponse, PlanRequest
from app.services.ai.factory import get_llm_provider
from app.services.content.planner import ContentPlanner, PlanningRequest

router = APIRouter(prefix="/content", tags=["content"])


def _planner() -> ContentPlanner:
    provider = os.getenv("LLM_PROVIDER", "mock")
    return ContentPlanner(
        get_llm_provider(
            provider=provider,
            base_url=os.getenv("LLM_BASE_URL"),
            model_id=os.getenv("LLM_MODEL_ID"),
            api_key=os.getenv("LLM_API_KEY"),
        )
    )


@router.post("/plan", response_model=ContentPlanResponse)
def create_content_plan(
    payload: PlanRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        plan = _planner().plan(
            PlanningRequest(
                source_text=payload.source_text,
                content_category=payload.content_category,
                language=payload.language,
                audience=payload.audience,
                tone=payload.tone,
                duration_seconds=payload.duration_seconds,
                video_type=payload.video_type,
            )
        )
        data = plan.model_dump()
        return {
            "title": data["title"],
            "hook": data["hook"],
            "summary": data["summary"],
            "audience": data["audience"],
            "language": data["language"],
            "tone": data["tone"],
            "characters": data["characters"],
            "style_bible": {
                "category": data["category"],
                "tone": data["tone"],
                "visual_style": "consistent cinematic style",
            },
            "scenes": [
                {
                    "number": scene["order"],
                    "duration_seconds": round(scene["duration_seconds"]),
                    "purpose": scene["continuity_notes"][0] if scene["continuity_notes"] else "Advance the story.",
                    "visual_prompt": scene["visual_prompt"],
                    "narration": scene["narration"],
                    "dialogue": scene["dialogue"],
                    "sound_effects": [],
                    "transition": scene["transition"],
                }
                for scene in data["scenes"]
            ],
        }
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
