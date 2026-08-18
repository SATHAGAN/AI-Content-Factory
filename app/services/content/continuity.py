from __future__ import annotations

from app.services.content.schemas import ContentPlan


def apply_continuity(plan: ContentPlan) -> ContentPlan:
    """Add stable visual constraints to every scene.

    This is model-agnostic: the same continuity data can be consumed by
    different image/video providers.
    """
    character_map={c.id:c for c in plan.characters}
    for scene in plan.scenes:
        for character_id in scene.characters:
            character=character_map.get(character_id)
            if character:
                traits=", ".join(character.visual_traits)
                scene.visual_prompt += f" Character consistency: {character.name}; {traits}."
        scene.continuity_notes.append(
            f"Maintain {plan.tone} tone and the established visual style."
        )
    return plan
