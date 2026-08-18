from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from app.services.vlm.interfaces import VLMRequest,VLMResult


class Qwen3VLWorker:
    """Adapter for a separately deployed Qwen3-VL inference worker.

    The worker is invoked through a command template and must return JSON.
    Keeping inference outside the API process makes model replacement easy.
    """

    def __init__(self, command: str | None = None):
        self.command=command or os.getenv("QWEN_VL_COMMAND","")

    def analyze(self, request: VLMRequest) -> VLMResult:
        if not self.command:
            raise RuntimeError("QWEN_VL_COMMAND is not configured")

        prompt_file=Path(os.getenv("VLM_PROMPT_DIR","./data/vlm"))/"prompt.txt"
        prompt_file.parent.mkdir(parents=True,exist_ok=True)
        prompt_file.write_text(request.prompt,encoding="utf-8")

        images_json=prompt_file.with_name("images.json")
        images_json.write_text(json.dumps(request.image_paths),encoding="utf-8")

        command=self.command.format(
            prompt_file=str(prompt_file),
            images_file=str(images_json),
        )
        result=subprocess.run(command,shell=True,capture_output=True,text=True,timeout=1800)
        if result.returncode != 0:
            raise RuntimeError(result.stderr[-4000:] or "Qwen3-VL inference failed")
        try:
            data=json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise RuntimeError("Qwen3-VL worker returned invalid JSON") from exc

        return VLMResult(
            provider="qwen3-vl",
            model_id=os.getenv("QWEN_VL_MODEL_ID","Qwen/Qwen3-VL-4B-Instruct"),
            scores={k:float(v) for k,v in data.get("scores",{}).items()},
            issues=list(data.get("issues",[])),
            decision=data.get("decision","manual_review"),
            raw=data,
        )
