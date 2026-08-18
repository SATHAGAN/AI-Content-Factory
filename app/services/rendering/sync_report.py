from __future__ import annotations

from dataclasses import asdict
from app.services.rendering.audio_timeline import AudioTimeline


def build_sync_report(timeline: AudioTimeline) -> dict:
    segments=[asdict(s) for s in timeline.segments]
    problematic=[
        s for s in segments
        if s["action"] in {"inspect_source","regenerate_or_recut"}
    ]
    return {
        "duration_seconds":timeline.duration_seconds,
        "scene_count":len(segments),
        "problem_count":len(problematic),
        "status":"pass" if not problematic else "review",
        "segments":segments,
    }
