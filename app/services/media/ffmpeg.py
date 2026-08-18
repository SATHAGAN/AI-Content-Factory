from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from app.services.media.models import (
    MediaOperation,
    MediaOperationRequest,
    MediaOperationResult,
)


class FFmpegMediaEngine:
    """Safe FFmpeg command builder/executor.

    Paths are passed as argument-list entries rather than shell strings, which
    prevents shell interpretation of user-controlled filenames.
    """

    def __init__(
        self,
        ffmpeg_binary: str = "ffmpeg",
        *,
        dry_run: bool = False,
    ):
        self.ffmpeg_binary = ffmpeg_binary
        self.dry_run = dry_run

    def available(self) -> bool:
        return shutil.which(self.ffmpeg_binary) is not None

    def _require_binary(self):
        if not self.available() and not self.dry_run:
            raise RuntimeError(
                f"{self.ffmpeg_binary} is required for media processing"
            )

    @staticmethod
    def _validate_output(path: str):
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)

    def build_command(self, request: MediaOperationRequest) -> list[str]:
        output = request.output_path
        self._validate_output(output)

        common = [
            self.ffmpeg_binary,
            "-hide_banner",
            "-loglevel", "error",
            "-y",
        ]

        if request.operation == MediaOperation.TRIM_VIDEO:
            if request.target_duration_seconds is None:
                raise ValueError("target_duration_seconds is required")
            return common + [
                "-i", request.input_path,
                "-t", str(request.target_duration_seconds),
                "-c", "copy",
                output,
            ]

        if request.operation == MediaOperation.EXTEND_VIDEO:
            if request.target_duration_seconds is None:
                raise ValueError("target_duration_seconds is required")
            return common + [
                "-stream_loop", "-1",
                "-i", request.input_path,
                "-t", str(request.target_duration_seconds),
                "-c", "copy",
                output,
            ]

        if request.operation == MediaOperation.ADJUST_AUDIO_SPEED:
            if request.speed is None or request.speed <= 0:
                raise ValueError("positive speed is required")
            # atempo accepts 0.5..2.0 per filter instance; this implementation
            # creates a safe chain for speeds outside that range.
            speed = float(request.speed)
            filters = []
            while speed > 2.0:
                filters.append("atempo=2.0")
                speed /= 2.0
            while speed < 0.5:
                filters.append("atempo=0.5")
                speed /= 0.5
            filters.append(f"atempo={speed:.8f}")
            return common + [
                "-i", request.input_path,
                "-filter:a", ",".join(filters),
                "-vn",
                output,
            ]

        if request.operation == MediaOperation.NORMALIZE_AUDIO:
            af = "loudnorm=I=-16:TP=-1.5:LRA=11"
            return common + [
                "-i", request.input_path,
                "-af", af,
                "-vn",
                output,
            ]

        if request.operation == MediaOperation.MERGE_AUDIO_VIDEO:
            if not request.video_path or not request.audio_path:
                raise ValueError("video_path and audio_path are required")
            return common + [
                "-i", request.video_path,
                "-i", request.audio_path,
                "-map", "0:v:0",
                "-map", "1:a:0",
                "-c:v", "copy",
                "-c:a", "aac",
                "-shortest",
                output,
            ]

        if request.operation == MediaOperation.EXTRACT_AUDIO:
            return common + [
                "-i", request.input_path,
                "-vn",
                "-c:a", "pcm_s16le",
                output,
            ]

        raise ValueError(f"Unsupported media operation: {request.operation}")

    def execute(self, request: MediaOperationRequest) -> MediaOperationResult:
        command = self.build_command(request)
        self._require_binary()

        if self.dry_run:
            return MediaOperationResult(
                operation=request.operation,
                output_path=request.output_path,
                duration_seconds=request.target_duration_seconds,
                command=tuple(command),
                metadata={"dry_run": True},
            )

        subprocess.run(command, check=True)
        if not Path(request.output_path).is_file():
            raise RuntimeError("FFmpeg completed but output artifact was not created")

        return MediaOperationResult(
            operation=request.operation,
            output_path=request.output_path,
            duration_seconds=request.target_duration_seconds,
            command=tuple(command),
            metadata={"dry_run": False},
        )


class FFmpegError(RuntimeError):
    """Backward-compatible FFmpeg execution error."""


class FFmpegRunner:
    """Compatibility facade over the Phase 52 FFmpegMediaEngine."""

    def __init__(self, binary: str = "ffmpeg", dry_run: bool = False):
        self.engine = FFmpegMediaEngine(
            ffmpeg_binary=binary,
            dry_run=dry_run,
        )

    @property
    def binary(self) -> str:
        return self.engine.ffmpeg_binary

    def available(self) -> bool:
        return self.engine.available()

    def concatenate(self, list_file, output):
        """Concatenate a prepared FFmpeg concat-demuxer list."""
        command = [
            self.binary,
            "-hide_banner",
            "-loglevel", "error",
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(list_file),
            "-c", "copy",
            str(output),
        ]
        return self.run(command)

    def run(self, command: list[str] | tuple[str, ...]):
        if self.engine.dry_run:
            return {"command": list(command), "dry_run": True}

        try:
            return subprocess.run(
                list(command),
                check=True,
                capture_output=True,
                text=True,
            )
        except (OSError, subprocess.CalledProcessError) as exc:
            raise FFmpegError(str(exc)) from exc
