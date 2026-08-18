from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class SourceType(str,Enum):
    TOPIC="topic"
    TRANSCRIPT="transcript"
    URL="url"
    FILE="file"
    GENERATED="generated"


@dataclass(frozen=True)
class ContentSource:
    source_id: str
    source_type: SourceType
    content: str
    title: str = ""
    language: str = "English"
    category: str = "general"
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class ContentRequest:
    source_type: SourceType
    content: str = ""
    title: str = ""
    language: str = "English"
    category: str = "general"
    target_duration_seconds: float = 60.0
    audience: str = "general"
    tone: str = "engaging"
    metadata: dict = field(default_factory=dict)
