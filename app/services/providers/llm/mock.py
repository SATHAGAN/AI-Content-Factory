from __future__ import annotations

from app.services.providers.contracts import LLMProvider, Scene


class MockLLMProvider:
    def plan(self, source_text: str, target_duration_seconds: int, category: str) -> list[Scene]:
        # Deterministic scene planning for integration tests.
        chunk = source_text.strip()[:500]
        count = max(1, min(3, round(target_duration_seconds / 60)))
        duration = max(5, target_duration_seconds / count)
        return [
            Scene(
                scene_id=f"scene_{i+1}",
                prompt=f"{category} cinematic scene: {chunk}",
                narration=chunk,
                duration_seconds=duration,
            )
            for i in range(count)
        ]
