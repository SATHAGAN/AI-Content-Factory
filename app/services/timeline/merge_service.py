from __future__ import annotations

from app.services.timeline.builder import TimelineBuilder
from app.services.timeline.ffmpeg import (
    build_concat_command,
    write_concat_manifest,
)
from app.services.timeline.validator import validate_timeline


class TimelineMergeService:
    def __init__(self, command_runner):
        self.command_runner=command_runner

    def prepare(self, clips, manifest_path, output_path):
        timeline=TimelineBuilder().build(clips)
        errors=validate_timeline(timeline,max_duration_seconds=600)
        if errors:
            raise ValueError("; ".join(errors))

        manifest=write_concat_manifest(timeline.clips,manifest_path)
        command=build_concat_command(manifest,output_path)

        return {
            "timeline":timeline,
            "manifest":manifest,
            "command":command,
        }

    def merge(self, clips, manifest_path, output_path):
        plan=self.prepare(clips,manifest_path,output_path)
        self.command_runner(plan["command"])
        return plan
