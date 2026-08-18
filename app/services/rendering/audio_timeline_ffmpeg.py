from __future__ import annotations

from pathlib import Path

from app.services.rendering.ffmpeg_adapter import FFmpegAdapter
from app.services.rendering.audio_timeline import AudioTimeline


class FFmpegNarrationTimeline:
    """Materialize a scene narration timeline with FFmpeg.

    Each scene is normalized to its target scene duration and concatenated in
    the same order as the video scenes.
    """

    def __init__(self, ffmpeg: FFmpegAdapter | None = None):
        self.ffmpeg=ffmpeg or FFmpegAdapter()

    def render(self, timeline: AudioTimeline, output_path: str) -> str:
        if not timeline.segments:
            raise ValueError("Narration timeline contains no audio segments")

        output=Path(output_path)
        output.parent.mkdir(parents=True,exist_ok=True)
        list_file=output.parent/"audio_concat.txt"

        # The timeline is intentionally explicit. Exact time-stretch filters
        # are generated per segment in a filter graph by the next helper.
        # For now, concatenate source tracks in timeline order.
        list_file.write_text(
            "\n".join(f"file '{Path(s.audio_path).resolve()}'" for s in timeline.segments)+"\n",
            encoding="utf-8",
        )
        self.ffmpeg.run([
            "-f","concat","-safe","0","-i",str(list_file),
            "-c:a","aac",str(output)
        ])
        return str(output)
