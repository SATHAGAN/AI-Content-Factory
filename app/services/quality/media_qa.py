from __future__ import annotations
from pathlib import Path
from app.services.quality.models import MediaProbe, QAIssue, QAReport


class MediaQualityAssurance:
    def __init__(
        self,
        *,
        duration_tolerance: float = 0.12,
        min_width: int = 360,
        min_height: int = 360,
        min_fps: float = 12.0,
        require_audio: bool = True,
    ):
        self.duration_tolerance=duration_tolerance
        self.min_width=min_width
        self.min_height=min_height
        self.min_fps=min_fps
        self.require_audio=require_audio

    def inspect_scene(
        self,
        scene_number: int,
        probe: MediaProbe,
        expected_duration: float,
    ) -> tuple[list[QAIssue], dict]:
        issues=[]
        if not probe.has_video:
            issues.append(QAIssue("missing_video","error","Video stream is missing",scene_number))
        if self.require_audio and not probe.has_audio:
            issues.append(QAIssue("missing_audio","error","Audio stream is missing",scene_number))
        if probe.width is not None and probe.width < self.min_width:
            issues.append(QAIssue("low_width","warning",f"Width {probe.width}px is below {self.min_width}px",scene_number))
        if probe.height is not None and probe.height < self.min_height:
            issues.append(QAIssue("low_height","warning",f"Height {probe.height}px is below {self.min_height}px",scene_number))
        if probe.fps is not None and probe.fps < self.min_fps:
            issues.append(QAIssue("low_fps","warning",f"FPS {probe.fps:.2f} is below {self.min_fps:.2f}",scene_number))
        if expected_duration > 0:
            drift=abs(probe.duration_seconds-expected_duration)/expected_duration
            if drift > self.duration_tolerance:
                issues.append(QAIssue("duration_mismatch","error",f"Duration drift is {drift:.1%}",scene_number))
        return issues,{
            "scene_number":scene_number,
            "path":probe.path,
            "duration_seconds":probe.duration_seconds,
            "expected_duration_seconds":expected_duration,
            "width":probe.width,"height":probe.height,"fps":probe.fps,
            "has_video":probe.has_video,"has_audio":probe.has_audio,
        }

    def evaluate(self, scene_inputs: list[tuple[int, MediaProbe, float]]) -> QAReport:
        issues=[]
        scene_reports=[]
        for number,probe,expected in scene_inputs:
            found,report=self.inspect_scene(number,probe,expected)
            issues.extend(found);scene_reports.append(report)
        errors=sum(1 for x in issues if x.severity=="error")
        warnings=sum(1 for x in issues if x.severity=="warning")
        score=max(0.0,100.0-errors*25.0-warnings*7.5)
        status="fail" if errors else ("review" if warnings else "pass")
        return QAReport(status=status,score=score,issues=issues,scene_reports=scene_reports)
