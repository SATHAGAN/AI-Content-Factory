from __future__ import annotations

import os

from dataclasses import dataclass

from app.services.publishing.factory import get_publisher
from app.services.publishing.interfaces import PublishRequest, PublishResult


@dataclass(frozen=True)
class MultiChannelPublishResult:
    results: list[PublishResult]
    errors: list[str]


class MultiChannelPublisher:
    def publish(self, targets: list[tuple[str, PublishRequest]]) -> MultiChannelPublishResult:
        results = []
        errors = []

        for platform, request in targets:
            try:
                publisher = get_publisher(
                    platform,
                    mock=os.getenv("PUBLISHER_PROVIDER","mock") == "mock",
                )
                results.append(publisher.publish(request))
            except Exception as exc:
                errors.append(f"{platform}: {exc}")

        return MultiChannelPublishResult(results, errors)
