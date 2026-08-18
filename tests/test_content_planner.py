from app.services.content.planner import ContentPlanner
from app.services.content.continuity import apply_continuity


def test_planner_creates_ordered_scenes():
    plan=ContentPlanner().plan(
        "A fox walks into a forest. The fox meets a bird. They help each other.",
        category="Kids", language="English", duration_seconds=60,
        tone="Warm", audience="Children"
    )
    assert plan.target_duration_seconds==60
    assert [s.order for s in plan.scenes]==list(range(1,len(plan.scenes)+1))
    assert abs(sum(s.duration_seconds for s in plan.scenes)-60)<0.01
    assert plan.characters


def test_continuity_adds_character_constraints():
    plan=ContentPlanner().plan(
        "A fox finds a friend.",
        category="Kids", language="English", duration_seconds=30,
        tone="Friendly"
    )
    plan=apply_continuity(plan)
    assert all("Character consistency" in s.visual_prompt for s in plan.scenes)
    assert all(s.continuity_notes for s in plan.scenes)


def test_non_kids_content_does_not_force_character():
    plan=ContentPlanner().plan(
        "Photosynthesis converts light energy into chemical energy.",
        category="Educational", language="English", duration_seconds=30,
        tone="Clear"
    )
    assert plan.characters==[]
