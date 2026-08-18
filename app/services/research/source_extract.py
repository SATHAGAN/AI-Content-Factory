from __future__ import annotations

import re


def extract_text_from_html(html: str) -> str:
    """Minimal deterministic HTML-to-text extractor.

    Production retrieval/parsing can replace this with a dedicated connector.
    """
    cleaned=re.sub(r"<script\b[^>]*>.*?</script>"," ",html,flags=re.I|re.S)
    cleaned=re.sub(r"<style\b[^>]*>.*?</style>"," ",cleaned,flags=re.I|re.S)
    cleaned=re.sub(r"<[^>]+>"," ",cleaned)
    cleaned=re.sub(r"\s+"," ",cleaned)
    return cleaned.strip()
