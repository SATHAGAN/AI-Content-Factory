from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="AI Content Factory GPU Worker", version="0.1.0")

MODEL_ID = os.getenv("VIDEO_MODEL_ID", "Wan-AI/Wan2.1-T2V-1.3B")
MODEL_BACKEND = os.getenv("VIDEO_MODEL_BACKEND", "wan-cli")
WAN_REPO = os.getenv("WAN_REPO", "/opt/Wan2.1")
WAN_CKPT = os.getenv("WAN_CKPT", "/models/Wan2.1-T2V-1.3B")


class GenerateRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=10000)
    output_path: str = "/outputs/scene.mp4"
    size: str = "832*480"
    frames: int = Field(default=81, ge=8, le=5000)
    seed: int | None = None


class GenerateResponse(BaseModel):
    status: str
    model_id: str
    output_path: str


@app.get("/health")
def health():
    try:
        import torch
        return {
            "status": "ok",
            "cuda_available": torch.cuda.is_available(),
            "gpu_count": torch.cuda.device_count(),
            "model_id": MODEL_ID,
        }
    except Exception as exc:
        return {"status": "degraded", "error": str(exc), "model_id": MODEL_ID}


@app.post("/generate", response_model=GenerateResponse)
def generate(request: GenerateRequest):
    if MODEL_BACKEND != "wan-cli":
        raise HTTPException(status_code=500, detail="Unsupported VIDEO_MODEL_BACKEND")

    output = Path(request.output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    command = [
        "python",
        f"{WAN_REPO}/generate.py",
        "--task",
        "t2v-1.3B",
        "--size",
        request.size,
        "--ckpt_dir",
        WAN_CKPT,
        "--prompt",
        request.prompt,
        "--offload_model",
        "True",
        "--t5_cpu",
        "--sample_shift",
        "8",
        "--sample_guide_scale",
        "6",
        "--frame_num",
        str(request.frames),
        "--save_file",
        str(output),
    ]
    if request.seed is not None:
        command.extend(["--base_seed", str(request.seed)])

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=int(os.getenv("GENERATION_TIMEOUT_SECONDS", "1800")),
        )
    except subprocess.TimeoutExpired as exc:
        raise HTTPException(status_code=504, detail="Generation timed out") from exc

    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=result.stderr[-5000:])

    if not output.exists():
        raise HTTPException(status_code=500, detail="Model finished without creating output")

    return GenerateResponse(status="succeeded", model_id=MODEL_ID, output_path=str(output))
