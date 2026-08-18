from __future__ import annotations
from dataclasses import dataclass, field


@dataclass(frozen=True)
class SourceReference:
    source_id: str
    title: str
    url: str | None = None
    publisher: str | None = None
    retrieved_at: str | None = None
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class ResearchClaim:
    claim_id: str
    text: str
    source_ids: tuple[str, ...]
    confidence: float
    importance: str = "normal"


@dataclass(frozen=True)
class ResearchPacket:
    topic: str
    summary: str
    claims: tuple[ResearchClaim, ...]
    sources: tuple[SourceReference, ...]
    research_required: bool = True
    metadata: dict = field(default_factory=dict)
