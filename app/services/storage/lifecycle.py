from __future__ import annotations

from datetime import datetime, timezone


class AssetKeyBuilder:
    """Stable, human-readable asset keys for multi-channel content."""

    def build(self, channel_id: str, job_id: str, asset_type: str, filename: str) -> str:
        safe=lambda x:"".join(c if c.isalnum() or c in "-_." else "_" for c in str(x))
        return f"{safe(channel_id)}/{safe(job_id)}/{safe(asset_type)}/{safe(filename)}"


class AssetLifecycle:
    PERMANENT={"final_video","thumbnail","subtitle","source"}
    TEMPORARY={"scene_video","scene_audio","frame","intermediate"}

    def is_permanent(self, asset_type: str) -> bool:
        return asset_type in self.PERMANENT

    def is_temporary(self, asset_type: str) -> bool:
        return asset_type in self.TEMPORARY

    def retention_class(self, asset_type: str) -> str:
        if self.is_permanent(asset_type):
            return "permanent"
        if self.is_temporary(asset_type):
            return "temporary"
        return "unknown"
