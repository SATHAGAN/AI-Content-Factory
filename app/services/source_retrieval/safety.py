from __future__ import annotations

from urllib.parse import urlparse


PRIVATE_HOSTS={
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "::1",
}


def reject_obvious_private_host(url: str) -> None:
    host=(urlparse(url).hostname or "").lower()
    if host in PRIVATE_HOSTS:
        raise ValueError("Private/local hosts are not allowed")
