from app.services.final_pipeline.models import PipelineResult,PipelineStatus
class FinalPipelineService:
    def __init__(self,scene_generator,visual_qa): self.scene_generator=scene_generator; self.visual_qa=visual_qa
    def generate_visuals(self,plan,job_id,*,kind,model=None):
        results=self.scene_generator.generate(plan,job_id=job_id,kind=kind,model=model)
        failures=[]
        for scene,result in zip(plan.scenes,results):
            qa=self.visual_qa.inspect(result.output_path,expected_duration=scene.duration_seconds,
                                      actual_duration=result.duration_seconds,prompt=scene.visual_prompt)
            if not qa.passed: failures.append(f"{scene.scene_id}: visual QA failed")
        status=PipelineStatus.MANUAL_REVIEW if failures else PipelineStatus.COMPLETED
        return PipelineResult(status,job_id,len(plan.scenes),len(results),tuple(failures))
