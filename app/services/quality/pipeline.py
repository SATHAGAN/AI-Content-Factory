from __future__ import annotations
from app.services.quality.ffprobe import FFprobeAdapter
from app.services.quality.media_qa import MediaQualityAssurance
from app.services.quality.regeneration import regeneration_plan


class MediaQAPipeline:
    def __init__(self, prober=None, qa=None):
        self.prober=prober or FFprobeAdapter()
        self.qa=qa or MediaQualityAssurance()

    def run(self, scenes: list[dict]) -> dict:
        inputs=[]
        for scene in scenes:
            path=scene["video_path"]
            probe=self.prober.probe(path)
            expected=float(scene.get("video_duration_seconds") or scene.get("duration_seconds") or 0)
            inputs.append((int(scene["number"]),probe,expected))
        report=self.qa.evaluate(inputs)
        result=report.to_dict()
        result["regeneration"]=regeneration_plan(report)
        return result
