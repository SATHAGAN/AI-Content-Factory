from __future__ import annotations


FACTUAL_CATEGORIES={"facts","educational","science","history","news","finance"}


def research_required(category: str, *, explicit: bool | None = None) -> bool:
    if explicit is not None:
        return explicit
    return category.strip().lower() in FACTUAL_CATEGORIES
