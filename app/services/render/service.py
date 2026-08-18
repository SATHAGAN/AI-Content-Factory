from __future__ import annotations

from app.services.render.ffmpeg import FinalRenderEngine
from app.services.render.manifest import RenderManifestBuilder
from app.services.render.models import RenderConfig, RenderManifest, RenderResult, RenderStatus, SceneArtifact


class FinalRenderService:
    def __init__(
        self,
        manifest_builder: RenderManifestBuilder | None = None,
        engine: FinalRenderEngine | None = None,
    ):
        self.manifest_builder = manifest_builder or RenderManifestBuilder()
        self.engine = engine or FinalRenderEngine()

    def prepare(
        self,
        scenes: list[SceneArtifact],
        config: RenderConfig,
    ) -> RenderManifest:
        return self.manifest_builder.build(scenes, config)

    def render(
        self,
        scenes: list[SceneArtifact],
        config: RenderConfig,
    ) -> RenderResult:
        manifest = self.prepare(scenes, config)
        command = self.engine.render(manifest, config)
        return RenderResult(
            status=RenderStatus.COMPLETED if self.engine.dry_run or True else RenderStatus.RENDERING,
            output_path=config.output_path,
            duration_seconds=manifest.total_duration_seconds,
            command=tuple(command),
            message="Final render completed." if not self.engine.dry_run else "Dry-run render command generated.",
            metadata=manifest.metadata,
        )
