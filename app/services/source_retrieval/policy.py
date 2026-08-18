from __future__ import annotations

from urllib.parse import urlparse


BLOCKED_SCHEMES={"file","ftp","javascript","data"}


def validate_url(url: str) -> None:
    parsed=urlparse(url)
    if parsed.scheme not in {"http","https"}:
        raise ValueError("Only HTTP and HTTPS URLs are allowed")
    if not parsed.netloc:
        raise ValueError("URL must contain a host")
    if parsed.scheme in BLOCKED_SCHEMES:
        raise ValueError(f"Blocked URL scheme: {parsed.scheme}")


def validate_content_type(content_type: str, allowed: tuple[str,...]) -> None:
    base=content_type.split(";",1)[0].strip().lower()
    if base not in {x.lower() for x in allowed}:
        raise ValueError(f"Unsupported content type: {base}")
