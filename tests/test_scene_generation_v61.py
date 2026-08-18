from app.services.scene_generation import SceneGenerationService
from app.services.scene_planner.models import SceneSpec, StoryPlan
from app.services.visuals import MockVisualProvider, VisualKind

def plan():
    return StoryPlan("Test","Hook","English","general",6,(
        SceneSpec("s1",1,"A","A visual",3,"A"),
        SceneSpec("s2",2,"B","B visual",3,"B"),
    ))

def test_scene_plan_generates_one_visual_per_scene(tmp_path):
    results=SceneGenerationService(MockVisualProvider(tmp_path)).generate(
        plan(),job_id="job-1",kind=VisualKind.VIDEO)
    assert len(results)==2
    assert [x.scene_id for x in results]==["s1","s2"]
    assert all(x.duration_seconds==3 for x in results)
