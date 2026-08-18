from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PlatformFormat:
    platform: str
    name: str
    width: int
    height: int
    max_duration_seconds: int | None
    aspect_ratio: str


FORMATS={
    "youtube_long":PlatformFormat("youtube","long",1920,1080,None,"16:9"),
    "youtube_short":PlatformFormat("youtube","short",1080,1920,180,"9:16"),
    "instagram_reel":PlatformFormat("instagram","reel",1080,1920,900,"9:16"),
    "instagram_feed":PlatformFormat("instagram","feed",1080,1350,900,"4:5"),
}


def get_platform_format(name: str) -> PlatformFormat:
    try:
        return FORMATS[name]
    except KeyError as exc:
        raise ValueError(f"Unsupported platform format: {name}") from exc
