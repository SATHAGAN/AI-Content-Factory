from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SubtitleLine:
    index: int
    start_seconds: float
    end_seconds: float
    text: str


def _timestamp(seconds: float) -> str:
    milliseconds = int(round(seconds * 1000))
    hours, rem = divmod(milliseconds, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    secs, ms = divmod(rem, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{ms:03}"


def build_srt(lines: list[SubtitleLine]) -> str:
    blocks = []
    for line in lines:
        if line.end_seconds <= line.start_seconds:
            raise ValueError("Subtitle end must be after start")
        blocks.append(
            f"{line.index}\n"
            f"{_timestamp(line.start_seconds)} --> {_timestamp(line.end_seconds)}\n"
            f"{line.text.strip()}\n"
        )
    return "\n".join(blocks)
