from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SubtitleCue:
    start_seconds: float
    end_seconds: float
    text: str


class SubtitleBuilder:
    def build(self, scenes: list[dict]) -> list[SubtitleCue]:
        cues=[]
        cursor=0.0
        for scene in sorted(scenes,key=lambda x:x["number"]):
            duration=float(scene.get("video_duration_seconds") or scene.get("duration_seconds") or 0)
            text=str(scene.get("narration","")).strip()
            if text and duration>0:
                cues.append(SubtitleCue(cursor,cursor+duration,text))
            cursor += duration
        return cues

    @staticmethod
    def _timestamp(seconds: float) -> str:
        milliseconds=round(seconds*1000)
        h,m=divmod(milliseconds,3600000)
        m,s=divmod(m,60000)
        s,ms=divmod(s,1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    def to_srt(self,cues: list[SubtitleCue]) -> str:
        blocks=[]
        for i,cue in enumerate(cues,1):
            blocks.append(
                f"{i}\n{self._timestamp(cue.start_seconds)} --> "
                f"{self._timestamp(cue.end_seconds)}\n{cue.text}\n"
            )
        return "\n".join(blocks)

    def write_srt(self, scenes: list[dict], output_path: str) -> str:
        from pathlib import Path
        path=Path(output_path)
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(self.to_srt(self.build(scenes)),encoding="utf-8")
        return str(path)
