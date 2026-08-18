from __future__ import annotations

from app.services.scene_planner.models import StoryPlan


def validate_story_plan(plan: StoryPlan, *, tolerance_seconds: float = 1.0) -> list[str]:
    errors=[]

    if not plan.title.strip():
        errors.append("Story title is empty")
    if not plan.scenes:
        errors.append("Story has no scenes")

    sequences=[scene.sequence for scene in plan.scenes]
    if sequences != list(range(1,len(sequences)+1)):
        errors.append("Scene sequences must be contiguous starting at 1")

    ids=[scene.scene_id for scene in plan.scenes]
    if len(ids) != len(set(ids)):
        errors.append("Scene IDs must be unique")

    for scene in plan.scenes:
        if not scene.narration.strip():
            errors.append(f"{scene.scene_id}: narration is empty")
        if not scene.visual_prompt.strip():
            errors.append(f"{scene.scene_id}: visual prompt is empty")
        if not scene.subtitle_text.strip():
            errors.append(f"{scene.scene_id}: subtitle text is empty")
        if scene.duration_seconds <= 0:
            errors.append(f"{scene.scene_id}: duration must be positive")

    if abs(plan.total_scene_duration-plan.target_duration_seconds) > tolerance_seconds:
        errors.append(
            f"Scene duration total {plan.total_scene_duration:.2f}s "
            f"does not match target {plan.target_duration_seconds:.2f}s"
        )

    return errors
