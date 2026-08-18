from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class QAThresholds:
    min_duration_seconds: float = 1.0
    max_silence_ratio: float = 0.45
    max_black_frame_ratio: float = 0.20
    max_frozen_frame_ratio: float = 0.30
    min_audio_peak_db: float = -45.0


@dataclass
class AdvancedQAResult:
    passed: bool
    duration_seconds: float | None = None
    has_audio: bool = False
    audio_duration_seconds: float | None = None
    silence_ratio: float | None = None
    black_frame_ratio: float | None = None
    frozen_frame_ratio: float | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "duration_seconds": self.duration_seconds,
            "has_audio": self.has_audio,
            "audio_duration_seconds": self.audio_duration_seconds,
            "silence_ratio": self.silence_ratio,
            "black_frame_ratio": self.black_frame_ratio,
            "frozen_frame_ratio": self.frozen_frame_ratio,
            "warnings": self.warnings,
            "errors": self.errors,
        }


class AdvancedVideoQA:
    """Deterministic media-level QA.

    This intentionally does not attempt semantic vision judging yet.
    Semantic consistency belongs to a later multimodal model stage.
    """

    def __init__(self, thresholds: QAThresholds | None = None):
        self.thresholds = thresholds or QAThresholds()

    def _probe(self, path: str) -> dict:
        if shutil.which("ffprobe") is None:
            raise RuntimeError("ffprobe not installed")

        result = subprocess.run(
            [
                "ffprobe", "-v", "error", "-show_streams", "-show_format",
                "-of", "json", path
            ],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode:
            raise RuntimeError(result.stderr.strip() or "ffprobe failed")
        return json.loads(result.stdout)

    def _filter_ratio(self, path: str, filter_name: str) -> float | None:
        if shutil.which("ffmpeg") is None:
            raise RuntimeError("ffmpeg not installed")

        # Metadata filters emit frame-level values. We parse their compact output.
        if filter_name == "blackdetect":
            vf = "blackdetect=d=0.1:pix_th=0.10"
            result = subprocess.run(
                ["ffmpeg", "-hide_banner", "-i", path, "-vf", vf, "-an", "-f", "null", "-"],
                capture_output=True, text=True, timeout=120,
            )
            if result.returncode:
                return None
            duration = self._duration_from_probe(path)
            if not duration:
                return None
            black = 0.0
            for line in result.stderr.splitlines():
                if "black_start:" in line and "black_end:" in line:
                    try:
                        start = float(line.split("black_start:", 1)[1].split()[0])
                        end = float(line.split("black_end:", 1)[1].split()[0])
                        black += max(0.0, end - start)
                    except (ValueError, IndexError):
                        pass
            return min(1.0, black / duration)

        if filter_name == "freezedetect":
            vf = "freezedetect=n=-60dB:d=0.5"
            result = subprocess.run(
                ["ffmpeg", "-hide_banner", "-i", path, "-vf", vf, "-an", "-f", "null", "-"],
                capture_output=True, text=True, timeout=120,
            )
            if result.returncode:
                return None
            duration = self._duration_from_probe(path)
            if not duration:
                return None
            frozen = 0.0
            for line in result.stderr.splitlines():
                if "freeze_start:" in line and "freeze_end:" in line:
                    try:
                        start = float(line.split("freeze_start:", 1)[1].split()[0])
                        end = float(line.split("freeze_end:", 1)[1].split()[0])
                        frozen += max(0.0, end - start)
                    except (ValueError, IndexError):
                        pass
            return min(1.0, frozen / duration)

        return None

    def _duration_from_probe(self, path: str) -> float | None:
        data = self._probe(path)
        value = data.get("format", {}).get("duration")
        return float(value) if value else None

    def _audio_silence_ratio(self, path: str) -> float | None:
        if shutil.which("ffmpeg") is None:
            raise RuntimeError("ffmpeg not installed")

        # silencedetect reports silence intervals to stderr.
        result = subprocess.run(
            [
                "ffmpeg", "-hide_banner", "-i", path,
                "-af", "silencedetect=noise=-45dB:d=0.4",
                "-vn", "-f", "null", "-"
            ],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode:
            return None

        duration = self._duration_from_probe(path)
        if not duration:
            return None

        silence = 0.0
        starts: list[float] = []
        for line in result.stderr.splitlines():
            if "silence_start:" in line:
                try:
                    starts.append(float(line.split("silence_start:", 1)[1].split()[0]))
                except (ValueError, IndexError):
                    pass
            elif "silence_end:" in line:
                try:
                    end = float(line.split("silence_end:", 1)[1].split()[0])
                    if starts:
                        silence += max(0.0, end - starts.pop())
                except (ValueError, IndexError):
                    pass

        return min(1.0, silence / duration)

    def check(self, path: str, require_audio: bool = True) -> AdvancedQAResult:
        result = AdvancedQAResult(passed=False)
        target = Path(path)

        if not target.exists():
            result.errors.append("video file not found")
            return result

        try:
            data = self._probe(path)
        except RuntimeError as exc:
            result.errors.append(str(exc))
            return result

        streams = data.get("streams", [])
        video = next((s for s in streams if s.get("codec_type") == "video"), None)
        audio = next((s for s in streams if s.get("codec_type") == "audio"), None)

        if not video:
            result.errors.append("missing video stream")
            return result

        duration = data.get("format", {}).get("duration")
        result.duration_seconds = float(duration) if duration else None
        result.has_audio = audio is not None
        if audio and audio.get("duration"):
            result.audio_duration_seconds = float(audio["duration"])

        if result.duration_seconds is None or result.duration_seconds < self.thresholds.min_duration_seconds:
            result.errors.append("video duration is too short")

        if require_audio and not result.has_audio:
            result.errors.append("audio stream is required")

        if result.has_audio:
            try:
                result.silence_ratio = self._audio_silence_ratio(path)
            except RuntimeError as exc:
                result.warnings.append(str(exc))
            if (
                result.silence_ratio is not None
                and result.silence_ratio > self.thresholds.max_silence_ratio
            ):
                result.errors.append("audio contains too much silence")

            if result.audio_duration_seconds and result.duration_seconds:
                delta = abs(result.audio_duration_seconds - result.duration_seconds)
                if delta > max(0.5, result.duration_seconds * 0.08):
                    result.errors.append(
                        f"audio/video duration mismatch: {delta:.2f}s"
                    )

        try:
            result.black_frame_ratio = self._filter_ratio(path, "blackdetect")
            result.frozen_frame_ratio = self._filter_ratio(path, "freezedetect")
        except RuntimeError as exc:
            result.warnings.append(str(exc))

        if (
            result.black_frame_ratio is not None
            and result.black_frame_ratio > self.thresholds.max_black_frame_ratio
        ):
            result.errors.append("excessive black-frame duration")

        if (
            result.frozen_frame_ratio is not None
            and result.frozen_frame_ratio > self.thresholds.max_frozen_frame_ratio
        ):
            result.errors.append("excessive frozen-frame duration")

        result.passed = not result.errors
        return result
