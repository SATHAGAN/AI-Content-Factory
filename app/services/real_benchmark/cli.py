from __future__ import annotations

import argparse
import json

from app.services.real_benchmark.config import VideoBenchmarkConfig
from app.services.real_benchmark.providers import DiffusersVideoProvider
from app.services.real_benchmark.runner import run_video_benchmark,validate_video_artifact


def main():
    parser=argparse.ArgumentParser(description="Real GPU video benchmark")
    parser.add_argument("--model",default=VideoBenchmarkConfig.model_id)
    parser.add_argument("--output",default=VideoBenchmarkConfig.output_path)
    parser.add_argument("--width",type=int,default=VideoBenchmarkConfig.width)
    parser.add_argument("--height",type=int,default=VideoBenchmarkConfig.height)
    parser.add_argument("--frames",type=int,default=VideoBenchmarkConfig.frames)
    parser.add_argument("--fps",type=int,default=VideoBenchmarkConfig.fps)
    args=parser.parse_args()

    config=VideoBenchmarkConfig(
        model_id=args.model,
        width=args.width,
        height=args.height,
        frames=args.frames,
        fps=args.fps,
        output_path=args.output,
    )
    provider=DiffusersVideoProvider(config.model_id)
    result=run_video_benchmark(provider,config)
    result["artifact"]=validate_video_artifact(result["output_path"])
    print(json.dumps(result,indent=2))


if __name__=="__main__":
    main()
