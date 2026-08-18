from __future__ import annotations


SYSTEM_PROMPT = """
You are the story and scene planner for an automated video production system.

Return ONLY valid JSON matching the supplied schema.

Rules:
- Create a coherent beginning, middle, and ending.
- Every scene must have narration and a visual prompt.
- Visual prompts must describe visible actions, subjects, environment, lighting,
  composition, and camera movement.
- Do not put dialogue in the visual prompt.
- Keep narration natural for text-to-speech.
- Keep scenes independently generatable.
- Respect the requested target duration.
- Avoid unsafe, sexual, violent, hateful, or age-inappropriate content when
  the audience is children.
""".strip()


def build_user_prompt(
    *,
    source_text: str,
    category: str,
    language: str,
    target_duration_seconds: float,
    scene_duration_seconds: float,
    audience: str,
    tone: str,
) -> str:
    return f"""
Source/topic:
{source_text}

Category: {category}
Language: {language}
Audience: {audience}
Tone: {tone}
Target duration: {target_duration_seconds} seconds
Target scene duration: {scene_duration_seconds} seconds

Create a complete story plan with approximately
{target_duration_seconds / scene_duration_seconds:.0f} scenes.

For every scene provide:
- scene_id
- sequence
- narration
- visual_prompt
- duration_seconds
- subtitle_text
- camera
- motion
- music_mood
""".strip()
