from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import quote

import httpx


class RemoteGPUClient:
    """HTTP client for the dedicated Wan GPU worker."""

    def __init__(self, base_url: str | None = None, timeout: float | None = None):
        self.base_url = (base_url or os.getenv("GPU_WORKER_URL", "")).rstrip("/")
        if not self.base_url:
            raise RuntimeError("GPU_WORKER_URL is required for production generation")
        self.timeout = timeout or float(os.getenv("GPU_WORKER_TIMEOUT_SECONDS", "1800"))
        self.headers = {}
        token = os.getenv("GPU_WORKER_TOKEN")
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    def health(self) -> dict:
        with httpx.Client(timeout=30, headers=self.headers) as client:
            response = client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()

    def generate_scene(self, *, job_id: str, scene: dict, scene_index: int) -> dict:
        frames = max(8, int(round(float(scene["duration_seconds"]) * int(scene.get("fps", 16)))))
        payload = {
            "prompt": scene["prompt"],
            "output_path": f"/outputs/{job_id}/scene_{scene_index:03d}.mp4",
            "size": os.getenv("GPU_VIDEO_SIZE", "832*480"),
            "frames": frames,
            "seed": scene.get("seed"),
        }
        with httpx.Client(timeout=self.timeout, headers=self.headers) as client:
            response = client.post(f"{self.base_url}/generate", json=payload)
            response.raise_for_status()
            return response.json()

    def generate_video(self, *, job_id: str, scenes: list[dict]) -> dict:
        generated = []
        for index, scene in enumerate(scenes, start=1):
            generated.append(
                self.generate_scene(job_id=job_id, scene=scene, scene_index=index)
            )
        return {
            "status": "succeeded",
            "model_id": generated[0].get("model_id") if generated else None,
            "scenes": generated,
            "output_path": generated[0].get("output_path") if generated else None,
            "duration_seconds": sum(float(s["duration_seconds"]) for s in scenes),
        }

    def download(self, remote_path: str, destination: Path) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        remote = quote(remote_path, safe="")
        with httpx.Client(timeout=self.timeout, headers=self.headers) as client:
            response = client.get(f"{self.base_url}/download?path={remote}")
            response.raise_for_status()
            destination.write_bytes(response.content)
