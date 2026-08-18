from app.services.production.models import ProductionJob
from app.services.production.pipeline import ProductionPipeline


class Planner:
    def plan(self,*args,**kwargs):
        return {"title":"Test Story","scenes":[{"number":1}]}


class Media:
    def generate(self,plan,job):
        return [{"number":1,"video_path":"scene.mp4"}]


class QA:
    def __init__(self,passed=True):
        self.passed=passed
    def evaluate(self,plan,scenes,job):
        return {"passed":self.passed,"score":90 if self.passed else 40}


class Finalizer:
    def render(self,plan,scenes,job):
        return {"video_path":"final.mp4"}


class Publisher:
    def publish(self,final,job):
        return [{"platform":"youtube","status":"published"}]


def make_pipeline(passed=True):
    return ProductionPipeline(
        planner=Planner(),
        media_generator=Media(),
        qa=QA(passed),
        finalizer=Finalizer(),
        publisher=Publisher(),
    )


def test_pipeline_runs_all_stages_in_order():
    result=make_pipeline().run(ProductionJob(
        job_id="job-1",
        channel_id="kids",
        content_type="youtube_short",
        category="kids",
        language="en",
        source_text="A fox helps a bird.",
    ))
    assert result.status=="completed"
    assert result.stages==[
        "planning",
        "media_generation",
        "quality_assurance",
        "finalization",
        "publishing",
    ]
    assert result.outputs["final"]["video_path"]=="final.mp4"


def test_failed_qa_stops_before_finalization():
    result=make_pipeline(False).run(ProductionJob(
        job_id="job-2",
        channel_id="kids",
        content_type="youtube_short",
        category="kids",
        language="en",
    ))
    assert result.status=="failed"
    assert "finalization" not in result.stages
    assert "QA rejected" in result.errors[0]


def test_failure_is_recorded_in_state():
    pipeline=make_pipeline(False)
    pipeline.run(ProductionJob(
        job_id="job-3",
        channel_id="kids",
        content_type="youtube_short",
        category="kids",
        language="en",
    ))
    state=pipeline.state.get("job-3")
    assert state.status=="failed"
    assert state.stage=="quality_assurance"
