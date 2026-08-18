from __future__ import annotations

from pathlib import Path

from app.services.subtitles.models import SubtitleArtifact, SubtitleFormat, SubtitleSegment


def _timestamp(seconds: float, vtt: bool = False) -> str:
    total_ms = max(0, round(seconds * 1000))
    hours, remainder = divmod(total_ms, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    separator = "." if vtt else ","
    return f"{hours:02d}:{minutes:02d}:{secs:02d}{separator}{millis:03d}"


class SubtitleWriter:
    def write(
        self,
        segments: list[SubtitleSegment],
        output_path: str,
        format: SubtitleFormat = SubtitleFormat.SRT,
    ) -> SubtitleArtifact:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        if format == SubtitleFormat.SRT:
            text = self._write_srt(segments)
        elif format == SubtitleFormat.VTT:
            text = self._write_vtt(segments)
        else:
            raise ValueError(f"Unsupported subtitle format: {format}")

        output.write_text(text, encoding="utf-8")
        duration = max((s.end_seconds for s in segments), default=0.0)
        return SubtitleArtifact(
            path=str(output),
            format=format,
            segment_count=len(segments),
            duration_seconds=duration,
            metadata={"encoding": "utf-8"},
        )

    def _write_srt(self, segments):
        blocks = []
        for segment in segments:
            blocks.append(
                f"{segment.index}\n"
                f"{_timestamp(segment.start_seconds)} --> "
                f"{_timestamp(segment.end_seconds)}\n"
                f"{segment.text}\n"
            )
        return "\n".join(blocks)

    def _write_vtt(self, segments):
        blocks = ["WEBVTT\n"]
        for segment in segments:
            blocks.append(
                f"{_timestamp(segment.start_seconds, True)} --> "
                f"{_timestamp(segment.end_seconds, True)}\n"
                f"{segment.text}\n"
            )
        return "\n".join(blocks)
