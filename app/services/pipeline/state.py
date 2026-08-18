from __future__ import annotations

from enum import StrEnum


class PipelineStage(StrEnum):
    QUEUED = "queued"
    PLANNING = "planning"
    GENERATING = "generating"
    VOICE = "voice"
    RENDERING = "rendering"
    MEDIA_QA = "media_qa"
    AI_JUDGE = "ai_judge"
    APPROVAL = "approval"
    SCHEDULED = "scheduled"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"


TERMINAL_STAGES = {
    PipelineStage.PUBLISHED,
    PipelineStage.FAILED,
}
