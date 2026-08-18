from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DeploymentConfig:
    environment: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    worker_count: int = 1
    scheduler_enabled: bool = False
    storage_provider: str = "local"
    inference_mode: str = "local"


def validate_production(config: DeploymentConfig) -> list[str]:
    errors=[]
    if config.environment=="production":
        if config.storage_provider=="local":
            errors.append("Production should use durable object storage, not local disk.")
        if config.scheduler_enabled is False:
            errors.append("Production scheduler must be explicitly enabled.")
        if config.worker_count < 1:
            errors.append("worker_count must be at least 1.")
    return errors
