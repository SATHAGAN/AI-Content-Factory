from __future__ import annotations


def build_judge_prompt(
    *,
    scene: dict,
    frame_paths: list[str],
    audio_transcript: str,
    criteria: list[str] | None = None,
) -> str:
    criteria=criteria or [
        "prompt alignment",
        "visual quality",
        "character consistency",
        "narration alignment",
        "continuity",
        "content safety",
    ]
    return f"""You are a strict video quality evaluator.

Evaluate this generated scene against its source plan.

Scene:
{scene}

Extracted frames:
{frame_paths}

Audio transcript:
{audio_transcript}

Criteria:
{criteria}

Return JSON only:
{{
  "scores": {{"criterion": 0-100}},
  "issues": [{{"criterion":"...", "severity":"error|warning", "message":"...", "evidence":"..."}}],
  "decision": "approve|regenerate|manual_review"
}}

Do not invent evidence that is not visible or present in the supplied inputs.
"""
