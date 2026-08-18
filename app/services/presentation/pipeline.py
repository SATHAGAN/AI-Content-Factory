from __future__ import annotations

from app.services.presentation.branding import BrandProfile, BrandingPolicy
from app.services.presentation.music import MusicPolicy
from app.services.presentation.subtitle_builder import SubtitleBuilder
from app.services.presentation.thumbnail import ThumbnailPlanBuilder


class PresentationPreparation:
    """Prepare platform-ready metadata/assets before final rendering."""

    def __init__(self, subtitle_builder=None, thumbnail_builder=None):
        self.subtitles=subtitle_builder or SubtitleBuilder()
        self.thumbnails=thumbnail_builder or ThumbnailPlanBuilder()
        self.music=MusicPolicy()
        self.branding=BrandingPolicy()

    def prepare(
        self,
        content_plan: dict,
        scenes: list[dict],
        *,
        brand: BrandProfile,
        platform_formats: list[str],
        music_enabled: bool = False,
        music_path: str | None = None,
    ) -> dict:
        self.branding.validate(brand)
        subtitle_path=None
        thumbnail_plans={}
        formats=[]

        from pathlib import Path
        out=Path("./data/presentation")
        out.mkdir(parents=True,exist_ok=True)

        subtitle_path=self.subtitles.write_srt(scenes,str(out/"subtitles.srt"))
        for name in platform_formats:
            from app.services.presentation.platform_formats import get_platform_format
            fmt=get_platform_format(name)
            formats.append(fmt.__dict__)

        for name in platform_formats:
            thumbnail_plans[name]=self.thumbnails.build(content_plan,platform=name)

        music=self.music.choose(
            content_plan.get("category","general"),
            music_enabled,
            music_path,
        )

        return {
            "subtitle_path":subtitle_path,
            "formats":formats,
            "thumbnail_plans":thumbnail_plans,
            "music":music,
            "brand":brand.__dict__,
        }
