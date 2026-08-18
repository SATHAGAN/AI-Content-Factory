from pathlib import Path

from app.services.e2e.smoke import SmokeArtifacts
from app.services.production.models import ProductionJob
from app.services.production.pipeline import ProductionPipeline
from app.services.e2e.contract import validate_production_result


class Planner:
    def plan(self,*args,**kwargs):
        return {
            "title":"Offline E2E Story",
            "scenes":[
                {"number":1,"narration":"Hello world.","duration_seconds":2}
            ],
        }


class Media:
    def __init__(self, artifacts):
        self.artifacts=artifacts
    def generate(self,plan,job):
        return [{
            "number":1,
            "video_path":self.artifacts.create_video("scene_001.mp4"),
            "audio_path":self.artifacts.create_audio("scene_001.wav"),
            "duration_seconds":2,
        }]


class QA:
    def evaluate(self,plan,scenes,job):
        return {"passed":True,"score":100,"checks":{"sync":True,"duration":True}}


class Finalizer:
    def __init__(self, artifacts):
        self.artifacts=artifacts
    def render(self,plan,scenes,job):
        return {
            "video_path":self.artifacts.create_video("final.mp4"),
            "subtitle_path":self.artifacts.create_subtitles(),
        }


class Publisher:
    def __init__(self):
        self.calls=[]
    def publish(self,final,job):
        self.calls.append((final,job.job_id))
        return [{"platform":p,"status":"published"} for p in job.platforms]


def test_complete_offline_pipeline(tmp_path):
    artifacts=SmokeArtifacts(str(tmp_path))
    publisher=Publisher()
    pipeline=ProductionPipeline(
        planner=Planner(),
        media_generator=Media(artifacts),
        qa=QA(),
        finalizer=Finalizer(artifacts),
        publisher=publisher,
    )
    result=pipeline.run(ProductionJob(
        job_id="e2e-001",
        channel_id="kids",
        content_type="youtube_short",
        category="kids",
        language="en",
        source_text="Hello world.",
        platforms=["youtube","instagram"],
    ))
    data=result.to_dict()
    assert validate_production_result(data)==[]
    assert Path(data["outputs"]["final"]["video_path"]).is_file()
    assert Path(data["outputs"]["final"]["subtitle_path"]).is_file()
    assert len(publisher.calls)==1


def test_smoke_artifacts_are_non_empty(tmp_path):
    artifacts=SmokeArtifacts(str(tmp_path))
    for path in [
        artifacts.create_video(),
        artifacts.create_audio(),
        artifacts.create_subtitles(),
    ]:
        assert Path(path).stat().st_size>0
