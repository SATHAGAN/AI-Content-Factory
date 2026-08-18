from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BrandProfile:
    name: str
    logo_path: str | None = None
    watermark_text: str | None = None
    intro_enabled: bool = False
    outro_enabled: bool = False


class BrandingPolicy:
    def validate(self, profile: BrandProfile) -> None:
        if not profile.name.strip():
            raise ValueError("Brand name is required")
        if profile.logo_path and not profile.logo_path.strip():
            raise ValueError("logo_path cannot be empty")
