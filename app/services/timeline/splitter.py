from __future__ import annotations


def split_duration(total_seconds: float, target_scene_seconds: float = 8.0) -> list[float]:
    if total_seconds <= 0:
        raise ValueError("total_seconds must be positive")
    if target_scene_seconds <= 0:
        raise ValueError("target_scene_seconds must be positive")

    result=[]
    remaining=total_seconds
    while remaining > 0:
        duration=min(target_scene_seconds,remaining)
        result.append(duration)
        remaining-=duration
    return result
