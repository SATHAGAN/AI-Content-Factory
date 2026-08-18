from __future__ import annotations

import json
from dataclasses import asdict

from app.services.model_catalog.catalog import DEFAULT_V1


def v1_profile_dict() -> dict:
    return asdict(DEFAULT_V1)


def write_v1_profile(path: str) -> str:
    from pathlib import Path
    target=Path(path)
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(
        json.dumps(v1_profile_dict(),indent=2,ensure_ascii=False),
        encoding="utf-8",
    )
    return str(target)
