from __future__ import annotations
from typing import Protocol
from app.services.publishing.models import PublishRequest, PublishResult


class Publisher(Protocol):
    platform: str
    def publish(self, request: PublishRequest) -> PublishResult:
        ...
