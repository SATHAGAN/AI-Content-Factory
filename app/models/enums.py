from enum import StrEnum


class JobStatus(StrEnum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class ApprovalMode(StrEnum):
    MANUAL = "manual"
    HYBRID = "hybrid"
    AUTOMATIC = "automatic"


class Platform(StrEnum):
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"


class SourceType(StrEnum):
    PROMPT = "prompt"
    TRANSCRIPT = "transcript"
    TEXT = "text"
    PDF = "pdf"
    DOCX = "docx"
    URL = "url"
    AUDIO = "audio"
    VIDEO = "video"


class ModelCapability(StrEnum):
    LLM = "llm"
    VIDEO = "video"
    IMAGE = "image"
    TTS = "tts"
    MUSIC = "music"
    MODERATION = "moderation"


class PublishStatus(StrEnum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    UPLOADING = "uploading"
    PUBLISHED = "published"
    FAILED = "failed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class ContentFormat(StrEnum):
    SHORT = "short"
    LONG = "long"
