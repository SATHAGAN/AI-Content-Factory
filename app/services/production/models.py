from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ProductionJob:
    job_id: str
    channel_id: str
    content_type: str
    category: str
    language: str
    title: str = ""
    source_text: str = ""
    platforms: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


@dataclass
class ProductionResult:
    job_id: str
    status: str
    stages: list[str] = field(default_factory=list)
    outputs: dict = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    def to_dict(self):
        return {
            "job_id": self.job_id,
            "status": self.status,
            "stages": self.stages,
            "outputs": self.outputs,
            "errors": self.errors,
        }
