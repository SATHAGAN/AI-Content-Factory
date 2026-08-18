from __future__ import annotations

from pathlib import Path


SUPPORTED_TEXT_EXTENSIONS={".txt",".md",".srt",".vtt",".json"}


def read_text_file(path: str) -> str:
    p=Path(path)
    if not p.is_file():
        raise FileNotFoundError(path)
    if p.suffix.lower() not in SUPPORTED_TEXT_EXTENSIONS:
        raise ValueError(f"Unsupported text source format: {p.suffix}")
    return p.read_text(encoding="utf-8")
