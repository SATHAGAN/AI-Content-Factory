from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.content.continuity import apply_continuity
from app.services.content.llm_planner import LLMContentPlanner

router=APIRouter(prefix="/content-planning",tags=["content-planning"])


class PlanRequest(BaseModel):
    source_text:str=Field(min_length=1,max_length=100000)
    category:str="General"
    language:str="English"
    duration_seconds:int=Field(default=60,ge=15,le=3600)
    tone:str="Engaging"
    audience:str="General audience"


@router.post("/plan")
def create_plan(payload:PlanRequest):
    plan=LLMContentPlanner().plan(
        payload.source_text,
        category=payload.category,
        language=payload.language,
        duration_seconds=payload.duration_seconds,
        tone=payload.tone,
        audience=payload.audience,
    )
    return apply_continuity(plan)
