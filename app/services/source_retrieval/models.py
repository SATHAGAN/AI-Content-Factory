from __future__ import annotations
from dataclasses import dataclass, field


@dataclass(frozen=True)
class RetrievedDocument:
    source_id: str
    url: str
    title: str
    text: str
    publisher: str | None = None
    content_type: str = "text/html"
    status_code: int = 200
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class RetrievalRequest:
    url: str
    timeout_seconds: float = 15.0
    max_bytes: int = 5_000_000
    allowed_content_types: tuple[str,...] = (
        "text/html",
        "text/plain",
        "application/json",
    )
