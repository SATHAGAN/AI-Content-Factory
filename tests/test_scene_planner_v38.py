from app.services.scene_planner.mock_llm import MockSceneLLM
from app.services.scene_planner.service import ScenePlannerService
from app.services.scene_planner.validator import validate_story_plan


def test_scene_planner_creates_valid_plan():
    plan=ScenePlannerService(MockSceneLLM()).plan(
        source_text="A little fox discovers a glowing forest.",
        category="kids",
        language="English",
        target_duration_seconds=40,
        scene_duration_seconds=8,
        audience="children",
        tone="warm",
    )
    assert plan.title=="Mock Story"
    assert len(plan.scenes)==5
    assert plan.total_scene_duration==40
    assert validate_story_plan(plan)==[]


def test_scene_plan_contains_generation_fields():
    plan=ScenePlannerService(MockSceneLLM()).plan(
        source_text="A science fact.",
        category="facts",
        language="English",
        target_duration_seconds=40,
    )
    for scene in plan.scenes:
        assert scene.narration
        assert scene.visual_prompt
        assert scene.subtitle_text
        assert scene.duration_seconds > 0
        assert scene.camera
        assert scene.motion


def test_invalid_plan_is_rejected():
    from app.services.scene_planner.models import SceneSpec,StoryPlan
    plan=StoryPlan(
        title="Broken",
        hook="",
        language="English",
        category="general",
        target_duration_seconds=10,
        scenes=(SceneSpec(
            scene_id="x",
            sequence=2,
            narration="",
            visual_prompt="",
            duration_seconds=2,
            subtitle_text="",
        ),),
    )
    errors=validate_story_plan(plan)
    assert errors
