from app.services.production.scheduled_runner import ScheduledProductionRunner


class Pipeline:
    def __init__(self):
        self.received=None
    def run(self,job):
        self.received=job
        return {"status":"completed"}


class Scheduler:
    pass


def test_scheduled_record_becomes_production_job():
    pipeline=Pipeline()
    runner=ScheduledProductionRunner(pipeline,Scheduler())
    result=runner.run_job({
        "job_id":"daily-001",
        "channel_id":"facts",
        "content_type":"youtube_short",
        "category":"facts",
        "language":"en",
        "source_text":"A science fact.",
        "platforms":["youtube","instagram"],
        "metadata":{"duration_seconds":45},
    })
    assert result["status"]=="completed"
    assert pipeline.received.job_id=="daily-001"
    assert pipeline.received.platforms==["youtube","instagram"]
    assert pipeline.received.metadata["duration_seconds"]==45
