from __future__ import annotations

from pathlib import Path


class ThumbnailPlanBuilder:
    def build(self, content_plan: dict, *, platform: str = "youtube") -> dict:
        title=content_plan.get("title","Untitled")
        hook=content_plan.get("hook","")
        return {
            "platform":platform,
            "headline":title[:80],
            "supporting_text":hook[:120],
            "source_scene":1,
            "generation_prompt":(
                f"Create a high-contrast thumbnail for '{title}'. "
                f"Show the main subject clearly. Supporting idea: {hook}"
            ),
        }


class ThumbnailArtifactWriter:
    def write_plan(self, plan: dict, output_path: str) -> str:
        import json
        path=Path(output_path)
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(plan,indent=2,ensure_ascii=False),encoding="utf-8")
        return str(path)
