from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from app.services.audio_mix.models import AudioMixConfig, AudioMixRequest, AudioMixResult


class AudioMixEngine:
    def __init__(self, binary: str = "ffmpeg", dry_run: bool = False):
        self.binary = binary
        self.dry_run = dry_run

    def available(self) -> bool:
        return shutil.which(self.binary) is not None

    @staticmethod
    def _validate_volume(value: float, name: str):
        if value < 0 or value > 4:
            raise ValueError(f"{name} must be between 0 and 4")

    def build_command(self, request: AudioMixRequest) -> list[str]:
        config = request.config
        self._validate_volume(config.voice_volume, "voice_volume")
        self._validate_volume(config.music_volume, "music_volume")
        self._validate_volume(config.ducked_music_volume, "ducked_music_volume")

        if not Path(request.video_path).is_file() and not self.dry_run:
            raise FileNotFoundError(request.video_path)
        if request.voice_path and not Path(request.voice_path).is_file() and not self.dry_run:
            raise FileNotFoundError(request.voice_path)
        if request.music_path and not Path(request.music_path).is_file() and not self.dry_run:
            raise FileNotFoundError(request.music_path)

        if not request.voice_path and not request.music_path:
            raise ValueError("At least voice_path or music_path is required")

        Path(request.output_path).parent.mkdir(parents=True, exist_ok=True)

        cmd = [
            self.binary, "-hide_banner", "-loglevel", "error", "-y",
            "-i", request.video_path,
        ]

        # The video already contains the visual stream. Additional inputs are
        # mapped as audio sources.
        if request.voice_path:
            cmd += ["-i", request.voice_path]
        if request.music_path:
            cmd += ["-i", request.music_path]

        filters: list[str] = []
        audio_labels: list[str] = []

        voice_input_index = 1
        music_input_index = 2 if request.voice_path else 1

        if request.voice_path:
            voice_filter = (
                f"[{voice_input_index}:a]volume={config.voice_volume:.4f}"
            )
            if config.normalize_voice:
                voice_filter += ",loudnorm=I=-16:TP=-1.5:LRA=11"
            voice_filter += "[voice]"
            filters.append(voice_filter)
            audio_labels.append("[voice]")

        if request.music_path:
            music_volume = (
                config.ducked_music_volume
                if config.music_ducking and request.voice_path
                else config.music_volume
            )
            music_filter = f"[{music_input_index}:a]volume={music_volume:.4f}"
            if config.normalize_music:
                music_filter += ",loudnorm=I=-24:TP=-2:LRA=11"
            music_filter += "[music]"
            filters.append(music_filter)
            audio_labels.append("[music]")

        if len(audio_labels) == 1:
            filters.append(f"{audio_labels[0]}anull[mixed]")
        else:
            filters.append(
                f"{audio_labels[0]}{audio_labels[1]}"
                "[amix=inputs=2:duration=longest:dropout_transition=2][mixed]"
            )

        cmd += [
            "-filter_complex", ";".join(filters),
            "-map", "0:v:0",
            "-map", "[mixed]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-ar", str(config.sample_rate),
            "-shortest",
            "-movflags", "+faststart",
            request.output_path,
        ]
        return cmd

    def execute(self, request: AudioMixRequest) -> AudioMixResult:
        command = self.build_command(request)

        if self.dry_run:
            return AudioMixResult(
                output_path=request.output_path,
                command=tuple(command),
                voice_enabled=bool(request.voice_path),
                music_enabled=bool(request.music_path),
                metadata={"dry_run": True},
            )

        if not self.available():
            raise RuntimeError("FFmpeg is required for audio mixing")

        subprocess.run(command, check=True)
        if not Path(request.output_path).is_file():
            raise RuntimeError("Audio mix completed without output artifact")

        return AudioMixResult(
            output_path=request.output_path,
            command=tuple(command),
            voice_enabled=bool(request.voice_path),
            music_enabled=bool(request.music_path),
            metadata={"dry_run": False},
        )
