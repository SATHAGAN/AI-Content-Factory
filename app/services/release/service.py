from dataclasses import dataclass
from pathlib import Path
import json
@dataclass(frozen=True)
class ReleaseManifest:
    job_id: str
    status: str
    scene_count: int
    visual_count: int
    artifacts: tuple[str,...]
    config: dict
class ReleaseService:
    def build_manifest(self,*,job_id,status,scene_count,visual_count,artifacts,config=None,output_path=None):
        m=ReleaseManifest(job_id,status,scene_count,visual_count,tuple(map(str,artifacts)),config or {})
        if output_path:
            p=Path(output_path);p.parent.mkdir(parents=True,exist_ok=True)
            p.write_text(json.dumps(m.__dict__,indent=2),encoding="utf-8")
        return m
