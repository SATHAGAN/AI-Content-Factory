from __future__ import annotations


def fit_audio_to_video(
    audio_duration_seconds: float,
    video_duration_seconds: float,
    *,
    min_speed: float = 0.90,
    max_speed: float = 1.10,
) -> dict:
    if audio_duration_seconds <= 0 or video_duration_seconds <= 0:
        raise ValueError("Durations must be positive")

    speed=audio_duration_seconds/video_duration_seconds
    speed=max(min_speed,min(max_speed,speed))

    return {
        "original_audio_duration":audio_duration_seconds,
        "target_video_duration":video_duration_seconds,
        "playback_speed":speed,
        "requires_adjustment":abs(speed-1.0)>1e-6,
    }
