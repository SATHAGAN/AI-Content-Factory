from __future__ import annotations


class RegenerationPromptRewriter:
    """Turn QA/Judge evidence into a more constrained scene prompt."""

    def rewrite(self, scene: dict, reasons: list[str], issues: list[dict] | None = None) -> str:
        base=scene.get("visual_prompt","").strip()
        constraints=[]
        for reason in reasons:
            r=reason.lower()
            if "prompt" in r or "alignment" in r:
                constraints.append("Follow the requested subject and action exactly.")
            if "character" in r:
                constraints.append("Preserve the established character appearance, clothing, proportions and colors.")
            if "continuity" in r:
                constraints.append("Match the preceding scene's setting, lighting, camera style and character state.")
            if "visual" in r or "quality" in r:
                constraints.append("Use a clean, stable composition with one clear focal subject and no malformed objects.")
            if "narration" in r:
                constraints.append("Ensure the visual action directly represents the narration.")
            if "safety" in r:
                constraints.append("Keep the scene age-appropriate and safe.")

        evidence=[x.get("message","") for x in (issues or []) if x.get("message")]
        suffix=" ".join(constraints)
        if evidence:
            suffix += " Avoid these detected problems: " + " ".join(evidence)
        return (base + " " + suffix).strip()
