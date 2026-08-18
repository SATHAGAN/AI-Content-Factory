from pydantic import BaseModel, Field


class ChannelCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    description: str | None = None
    default_language: str = Field(default="en", min_length=2, max_length=32)
    daily_shorts_target: int = Field(default=0, ge=0)
    daily_long_target: int = Field(default=0, ge=0)


class ChannelResponse(BaseModel):
    id: str
    name: str
    description: str | None
    default_language: str
    approval_mode: str
    daily_shorts_target: int
    daily_long_target: int


class ContentProfileCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    category: str = Field(min_length=1, max_length=100)
    audience: str | None = None
    language: str = Field(default="en", min_length=2, max_length=32)
    tone: str | None = None
    settings: dict = Field(default_factory=dict)


class ContentProfileResponse(BaseModel):
    id: str
    name: str
    category: str
    audience: str | None
    language: str
    tone: str | None
    settings: dict


class SourceCreate(BaseModel):
    source_type: str
    title: str | None = None
    content_text: str | None = None
    storage_uri: str | None = None
    metadata: dict = Field(default_factory=dict)


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    channel_id: str | None = None
    content_profile_id: str | None = None
    source_document_id: str | None = None
    settings: dict = Field(default_factory=dict)


class ProjectResponse(BaseModel):
    id: str
    name: str
    status: str
    channel_id: str | None
    content_profile_id: str | None
    source_document_id: str | None
    settings: dict
