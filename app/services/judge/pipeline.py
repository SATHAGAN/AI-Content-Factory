from __future__ import annotations
from app.services.judge.factory import get_judge


class AIJudgePipeline:
    def __init__(self, judge=None):
        self.judge=judge or get_judge()

    def evaluate(self, scenes: list[dict], media_qa_by_scene: dict[int,dict] | None = None, safety_by_scene: dict[int,dict] | None = None):
        reports=[]
        for scene in sorted(scenes,key=lambda x:x["number"]):
            n=int(scene["number"])
            report=self.judge.evaluate_scene(
                scene,
                media_qa=(media_qa_by_scene or {}).get(n),
                safety=(safety_by_scene or {}).get(n),
            )
            reports.append(report.to_dict())

        if any(r["decision"]=="regenerate" for r in reports):
            decision="regenerate"
        else:
            decision="approve"

        scene_numbers=sorted({
            n for r in reports for n in r["regeneration"]["scene_numbers"]
            if n is not None
        })
        return {
            "decision":decision,
            "scene_count":len(reports),
            "reports":reports,
            "regeneration":{
                "required":bool(scene_numbers),
                "scene_numbers":scene_numbers,
                "reasons":sorted({
                    reason
                    for r in reports
                    for reason in r["regeneration"]["reasons"]
                }),
            },
        }
