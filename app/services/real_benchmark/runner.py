from __future__ import annotations

import json
import time
from pathlib import Path


def run_video_benchmark(provider, config):
    start=time.perf_counter()
    path=provider.generate(
        prompt=config.prompt,
        width=config.width,
        height=config.height,
        frames=config.frames,
        fps=config.fps,
        output_path=config.output_path,
    )
    elapsed=time.perf_counter()-start

    result={
        "task":"video",
        "model_id":config.model_id,
        "output_path":path,
        "elapsed_seconds":round(elapsed,3),
        "frames":config.frames,
        "fps":config.fps,
        "resolution":[config.width,config.height],
        "duration_seconds":round(config.frames/config.fps,3),
    }
    Path(config.output_path).with_suffix(".benchmark.json").write_text(
        json.dumps(result,indent=2),
        encoding="utf-8",
    )
    return result


def validate_video_artifact(path: str) -> dict:
    p=Path(path)
    if not p.is_file():
        return {"valid":False,"reason":"file does not exist"}
    if p.stat().st_size==0:
        return {"valid":False,"reason":"file is empty"}
    return {"valid":True,"size_bytes":p.stat().st_size}
