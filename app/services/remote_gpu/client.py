from __future__ import annotations

import os
from pathlib import Path

import httpx


class RemoteGPUError(RuntimeError):
    pass


class RemoteGPUClient:
    def __init__(self, base_url: str | None = None, token: str | None = None):
        self.base_url = (base_url or os.getenv("GPU_WORKER_URL", "")).rstrip("/")
        self.token = token or os.getenv("GPU_WORKER_TOKEN", "")
        if not self.base_url:
            raise RemoteGPUError("GPU_WORKER_URL is not configured")
        if not self.token:
            raise RemoteGPUError("GPU_WORKER_TOKEN is not configured")

    @property
    def headers(self) -> dict[str, str]:
        return {"X-Worker-Token": self.token}

    def health(self) -> dict:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()

    def generate_video(self, *, job_id: str, scenes: list[dict]) -> dict:
        payload = {"job_id": job_id, "scenes": scenes}
        with httpx.Client(timeout=3600.0) as client:
            response = client.post(
                f"{self.base_url}/generate-video",
                json=payload,
                headers=self.headers,
            )
            if response.status_code >= 400:
                raise RemoteGPUError(response.text[-5000:])
            return response.json()

    def download(self, remote_path: str, destination: str | Path) -> Path:
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)

        with httpx.Client(timeout=3600.0) as client:
            with client.stream(
                "GET",
                f"{self.base_url}/download",
                params={"path": remote_path},
                headers=self.headers,
            ) as response:
                if response.status_code >= 400:
                    raise RemoteGPUError(response.text[:5000])
                with destination.open("wb") as output:
                    for chunk in response.iter_bytes():
                        output.write(chunk)

        return destination
