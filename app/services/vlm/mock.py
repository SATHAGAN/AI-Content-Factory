from __future__ import annotations
from app.services.vlm.interfaces import VLMRequest,VLMResult


class MockVLM:
    provider="mock"
    model_id="mock-vlm-v1"

    def analyze(self, request: VLMRequest) -> VLMResult:
        return VLMResult(
            provider=self.provider,
            model_id=self.model_id,
            scores={
                "prompt_alignment":90.0,
                "visual_quality":90.0,
                "character_consistency":90.0,
                "narration_alignment":90.0,
                "continuity":90.0,
            },
            issues=[],
            decision="approve",
            raw={"frame_count":len(request.image_paths)},
        )
