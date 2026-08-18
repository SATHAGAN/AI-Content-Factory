from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AudioSegment:
    scene_number: int
    audio_path: str
    start_seconds: float
    duration_seconds: float
    source_duration_seconds: float
    speed_factor: float
    action: str


@dataclass(frozen=True)
class AudioTimeline:
    segments: list[AudioSegment]
    duration_seconds: float


class AudioTimelineBuilder:
    """Build a deterministic narration timeline from per-scene audio files.

    No audio is dropped. Each segment receives an explicit start time and
    timing decision. The actual time-stretch operation is delegated to FFmpeg.
    """

    def build(self, scene_assets: list[dict]) -> AudioTimeline:
        ordered=sorted(scene_assets,key=lambda x:x["number"])
        cursor=0.0
        segments=[]

        for asset in ordered:
            # No narration means this scene does not need an audio segment.
            if not asset.get("audio_path"):
                continue
            if "video_duration_seconds" not in asset:
                raise RuntimeError(
                    "Multiple scene audio tracks require narration timeline assembly "
                    "with measured video durations"
                )
            target=float(asset["video_duration_seconds"])
            source=max(float(asset.get("audio_duration_seconds",0.0)),0.0)

            if source <= 0:
                action="inspect_source"
                speed=1.0
            else:
                ratio=source/target if target>0 else 1.0
                if 0.95 <= ratio <= 1.05:
                    action="keep"
                    speed=1.0
                elif ratio <= 1.25:
                    action="time_stretch"
                    speed=ratio
                else:
                    action="regenerate_or_recut"
                    speed=ratio

            segments.append(AudioSegment(
                scene_number=int(asset["number"]),
                audio_path=str(asset["audio_path"]),
                start_seconds=cursor,
                duration_seconds=target,
                source_duration_seconds=source,
                speed_factor=speed,
                action=action,
            ))
            cursor += target

        return AudioTimeline(segments=segments,duration_seconds=cursor)
