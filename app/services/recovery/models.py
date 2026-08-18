from __future__ import annotations
from dataclasses import dataclass, field


@dataclass(frozen=True)
class RegenerationAttempt:
    scene_number: int
    attempt: int
    reason: str
    prompt: str
    status: str


@dataclass
class RecoveryResult:
    status: str
    attempts: list[RegenerationAttempt] = field(default_factory=list)
    final_scene_numbers: list[int] = field(default_factory=list)
    manual_review_scenes: list[int] = field(default_factory=list)

    def to_dict(self):
        return {
            "status": self.status,
            "attempts": [a.__dict__ for a in self.attempts],
            "final_scene_numbers": self.final_scene_numbers,
            "manual_review_scenes": self.manual_review_scenes,
        }
