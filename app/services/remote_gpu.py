from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import quote

import httpx


class RemoteGPUClient:
    """HTTP client for the dedicated Wan/Qwen GPU worker."""

    def __init__(self, base_url: str | None = None, timeout: float | None = None):
        self.base_url = (base_url or os.getenv("GPU_WORKER_URL", "")).rstrip("/")
        if not self.base_url:
            raise RuntimeError("GPU_WORKER_URL is required for production generation")
        self.timeout = timeout or float(os.getenv("GPU_WORKER_TIMEOUT_SECONDS", "3600"))
        self.headers: dict[str, str] = {}
        token = os.getenv("GPU_WORKER_TOKEN")
        if token:
            self.headers["X-Worker-Token"] = token

    def health(self) -> dict:
        with httpx.Client(timeout=30, headers=self.headers) as client:
            response = client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()

    def generate_video(self, *, job_id: str, scenes: list[dict]) -> dict:
        payload = {"job_id": job_id, "scenes": scenes}
        with httpx.Client(timeout=self.timeout, headers=self.headers) as client:
            response = client.post(f"{self.base_url}/generate-video", json=payload)
            response.raise_for_status()
            return response.json()

    def download(self, remote_path: str, destination: Path) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        remote = quote(remote_path, safe="")
        with httpx.Client(timeout=self.timeout, headers=self.headers) as client:
            response = client.get(f"{self.base_url}/download?path={remote}")
            response.raise_for_status()
            destination.write_bytes(response.content)
