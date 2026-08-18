from __future__ import annotations

from app.services.timeline.models import Timeline


def validate_timeline(
    timeline: Timeline,
    *,
    max_duration_seconds: float | None = None,
) -> list[str]:
    errors=[]
    seen=set()

    for clip in timeline.clips:
        if clip.scene_id in seen:
            errors.append(f"Duplicate scene id: {clip.scene_id}")
        seen.add(clip.scene_id)

        if clip.duration_seconds <= 0:
            errors.append(f"Non-positive duration: {clip.scene_id}")

    if max_duration_seconds is not None and timeline.total_duration_seconds > max_duration_seconds:
        errors.append(
            f"Timeline exceeds maximum duration: "
            f"{timeline.total_duration_seconds:.2f}s > {max_duration_seconds:.2f}s"
        )

    return errors
