from dataclasses import dataclass
from enum import Enum
class PipelineStatus(str,Enum):
    COMPLETED="completed"; MANUAL_REVIEW="manual_review"; FAILED="failed"
@dataclass(frozen=True)
class PipelineResult:
    status: PipelineStatus
    job_id: str
    scene_count: int
    visual_count: int
    failures: tuple[str,...]=()
