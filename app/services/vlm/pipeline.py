from __future__ import annotations

from pathlib import Path

from app.services.vlm.factory import get_vlm
from app.services.vlm.interfaces import VLMRequest


class VLMJudgePipeline:
    def __init__(self, vlm=None, frame_extractor=None):
        self.vlm=vlm or get_vlm()
        self.frame_extractor=frame_extractor

    def evaluate_scene(
        self,
        scene: dict,
        *,
        frame_paths: list[str] | None = None,
        frame_output_dir: str = "./data/vlm_frames",
        sample_fps: float = 1.0,
        max_frames: int = 12,
    ) -> dict:
        if frame_paths is None:
            if self.frame_extractor is None:
                raise RuntimeError("frame_extractor is required when frame_paths are not supplied")
            frame_paths=self.frame_extractor.extract(
                scene["video_path"],frame_output_dir,
                fps=sample_fps,max_frames=max_frames,
            )

        if not frame_paths:
            raise RuntimeError("No frames available for VLM evaluation")

        prompt=f"""Evaluate this generated video scene.

Source visual prompt:
{scene.get("visual_prompt","")}

Narration:
{scene.get("narration","")}

Evaluate only from the supplied frames and text. Score:
- prompt_alignment
- visual_quality
- character_consistency
- narration_alignment
- continuity

Return structured JSON with scores from 0 to 100, issues, and:
approve, regenerate, or manual_review.
"""
        result=self.vlm.analyze(VLMRequest(prompt=prompt,image_paths=frame_paths))
        return {
            "scene_number":scene["number"],
            "provider":result.provider,
            "model_id":result.model_id,
            "scores":result.scores,
            "issues":result.issues,
            "decision":result.decision,
            "frame_count":len(frame_paths),
            "frame_paths":frame_paths,
            "raw":result.raw,
        }
