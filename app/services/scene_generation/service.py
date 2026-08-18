from app.services.scene_planner.models import StoryPlan
from app.services.visuals import VisualKind, VisualRequest

class SceneGenerationService:
    def __init__(self, visual_provider):
        self.visual_provider=visual_provider

    def generate(self, plan: StoryPlan, *, job_id: str, kind: VisualKind=VisualKind.VIDEO,
                 width=1080, height=1920, fps=24, model=None):
        results=[]
        for scene in plan.scenes:
            request=VisualRequest(
                job_id=job_id, scene_id=scene.scene_id, prompt=scene.visual_prompt,
                duration_seconds=scene.duration_seconds, width=width, height=height,
                fps=fps, model=model, kind=kind,
                metadata={"sequence":scene.sequence,"camera":scene.camera,"motion":scene.motion}
            )
            results.append(self.visual_provider.generate(request))
        return tuple(results)
