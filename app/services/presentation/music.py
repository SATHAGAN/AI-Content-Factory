from __future__ import annotations

from pathlib import Path


class MusicPolicy:
    def __init__(self, default_volume: float = 0.10):
        self.default_volume=max(0.0,min(1.0,default_volume))

    def choose(self, category: str, enabled: bool, music_path: str | None) -> dict:
        if not enabled or not music_path:
            return {"enabled":False,"path":None,"volume":0.0}
        if not Path(music_path).exists():
            raise FileNotFoundError(music_path)
        return {
            "enabled":True,
            "path":music_path,
            "volume":self.default_volume,
            "category":category,
        }
