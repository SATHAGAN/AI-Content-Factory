from __future__ import annotations

from pathlib import Path


class SmokeArtifacts:
    """Creates deterministic tiny artifacts for an offline end-to-end test."""

    def __init__(self, root: str):
        self.root=Path(root)
        self.root.mkdir(parents=True,exist_ok=True)

    def create_video(self, name="final.mp4") -> str:
        path=self.root/name
        path.write_bytes(b"FAKE-MP4-ARTIFACT")
        return str(path)

    def create_audio(self, name="voice.wav") -> str:
        path=self.root/name
        path.write_bytes(b"FAKE-WAV-ARTIFACT")
        return str(path)

    def create_subtitles(self, name="subtitles.srt") -> str:
        path=self.root/name
        path.write_text(
            "1\n00:00:00,000 --> 00:00:02,000\nHello world.\n",
            encoding="utf-8",
        )
        return str(path)
