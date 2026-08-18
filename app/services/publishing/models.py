from __future__ import annotations
from dataclasses import dataclass, field


@dataclass(frozen=True)
class PublishRequest:
    channel_id: str = ""
    platform: str = ""
    video_path: str | None = None
    title: str = ""
    description: str = ""
    tags: list[str] = field(default_factory=list)
    privacy_status: str = "private"
    publish_at: str | None = None
    thumbnail_path: str | None = None
    metadata: dict = field(default_factory=dict)
    # Legacy API compatibility fields
    media_uri: str | None = None
    caption: str | None = None
    privacy: str | None = None

    def __post_init__(self):
        if self.video_path is None and self.media_uri:
            object.__setattr__(self, "video_path", self.media_uri)
        if not self.description and self.caption:
            object.__setattr__(self, "description", self.caption)
        if self.privacy_status == "private" and self.privacy:
            object.__setattr__(self, "privacy_status", self.privacy)



@dataclass(frozen=True)
class PublishResult:
    platform: str
    status: str
    remote_id: str | None = None
    external_post_id: str | None = None
    url: str | None = None
    message: str = ""
    raw: dict = field(default_factory=dict)
