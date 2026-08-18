from __future__ import annotations
from dataclasses import dataclass, field


@dataclass(frozen=True)
class MediaProbe:
    path: str
    duration_seconds: float
    width: int | None = None
    height: int | None = None
    fps: float | None = None
    has_video: bool = False
    has_audio: bool = False


@dataclass(frozen=True)
class QAIssue:
    code: str
    severity: str
    message: str
    scene_number: int | None = None


@dataclass
class QAReport:
    status: str
    score: float
    issues: list[QAIssue] = field(default_factory=list)
    scene_reports: list[dict] = field(default_factory=list)

    def to_dict(self):
        return {
            "status": self.status,
            "score": self.score,
            "issues": [x.__dict__ for x in self.issues],
            "scene_reports": self.scene_reports,
        }
