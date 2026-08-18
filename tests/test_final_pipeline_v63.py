from app.services.final_pipeline import FinalPipelineService,PipelineStatus
from app.services.scene_generation import SceneGenerationService
from app.services.scene_planner.models import SceneSpec,StoryPlan
from app.services.visual_qa import VisualQAService
from app.services.visuals import MockVisualProvider
from app.services.visuals import VisualKind
def make_plan():
    return StoryPlan("T","H","English","general",4,(SceneSpec("s1",1,"n","visual",2,"n"),SceneSpec("s2",2,"n","visual",2,"n")))
def test_visual_stage_completes(tmp_path):
    r=FinalPipelineService(SceneGenerationService(MockVisualProvider(tmp_path)),VisualQAService()).generate_visuals(
        make_plan(),"job",kind=VisualKind.VIDEO)
    assert r.status==PipelineStatus.COMPLETED and r.visual_count==2
def test_visual_stage_surfaces_review(tmp_path):
    class BadQA(VisualQAService):
        def inspect(self,*a,**k):
            from app.services.visual_qa import VisualQAResult
            return VisualQAResult(False,.1,("bad",),True)
    r=FinalPipelineService(SceneGenerationService(MockVisualProvider(tmp_path)),BadQA()).generate_visuals(
        make_plan(),"job",kind=VisualKind.VIDEO)
    assert r.status==PipelineStatus.MANUAL_REVIEW and r.failures
