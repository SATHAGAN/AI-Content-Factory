from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from app.services.media.ffmpeg import FFmpegRunner
from app.services.render.models import RenderConfig, RenderManifest


class FinalRenderEngine:
    def __init__(self, binary: str = "ffmpeg", dry_run: bool = False):
        self.runner = FFmpegRunner(binary=binary, dry_run=dry_run)
        self.binary = binary
        self.dry_run = dry_run

    def available(self) -> bool:
        return shutil.which(self.binary) is not None

    def build_concat_command(
        self,
        manifest_file: str,
        config: RenderConfig,
    ) -> list[str]:
        Path(config.output_path).parent.mkdir(parents=True, exist_ok=True)
        return [
            self.binary,
            "-hide_banner",
            "-loglevel", "error",
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", manifest_file,
            "-c:v", config.video_codec,
            "-preset", config.preset,
            "-crf", str(config.crf),
            "-c:a", config.audio_codec,
            "-movflags", "+faststart",
            config.output_path,
        ]

    def render(self, manifest: RenderManifest, config: RenderConfig):
        concat_file = Path(config.output_path).with_suffix(".concat.txt")
        concat_file.parent.mkdir(parents=True, exist_ok=True)

        lines = []
        for scene in manifest.scenes:
            # concat demuxer syntax; paths are escaped for single-quoted entries.
            escaped = scene.video_path.replace("'", r"'\''")
            lines.append(f"file '{escaped}'")
        concat_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

        command = self.build_concat_command(str(concat_file), config)

        if self.dry_run:
            return command

        if not self.available():
            raise RuntimeError("FFmpeg is required for final rendering")

        subprocess.run(command, check=True)
        if not Path(config.output_path).is_file():
            raise RuntimeError("Final render completed without output artifact")
        return command
