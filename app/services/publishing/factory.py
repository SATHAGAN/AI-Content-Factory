from __future__ import annotations

import os

from app.services.publishing.providers.mock import MockPublisher
from app.services.publishing.providers.youtube import YouTubePublisher
from app.services.publishing.providers.instagram import InstagramPublisher


def get_publisher(platform: str, *, service=None, client=None, media_uploader=None, mock: bool=False):
    if mock:
        return MockPublisher(platform)
    if platform=="youtube":
        return YouTubePublisher(service=service, media_uploader=media_uploader)
    if platform=="instagram":
        return InstagramPublisher(client=client)
    raise ValueError(f"Unsupported platform: {platform}")
