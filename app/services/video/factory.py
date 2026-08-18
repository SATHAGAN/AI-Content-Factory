from __future__ import annotations

from app.services.video.mock import MockVideoProvider, MockVideoGenerator
from app.services.video.models import VideoProvider


def create_video_provider(provider: VideoProvider | str = VideoProvider.MOCK, **kwargs):
    provider = VideoProvider(provider)

    if provider == VideoProvider.MOCK:
        return MockVideoGenerator(
            output_root=kwargs.get("output_root", "artifacts/video")
        )

    if provider in {VideoProvider.LOCAL, VideoProvider.REMOTE}:
        raise RuntimeError(
            f"Provider '{provider.value}' is reserved for a concrete adapter. "
            "Install/configure the corresponding model backend before enabling it."
        )

    raise ValueError(f"Unsupported video provider: {provider}")


# Backward-compatible factory used by earlier media orchestration code.
def get_video_generator(provider: str = "mock", **kwargs):
    return create_video_provider(provider, **kwargs)


def get_video_provider(provider: str | None = None, **kwargs):
    import os
    return create_video_provider(
        provider or os.getenv("VIDEO_PROVIDER", "mock"),
        **kwargs,
    )
