from __future__ import annotations

import urllib.request

from app.services.research.source_extract import extract_text_from_html
from app.services.source_retrieval.models import RetrievedDocument,RetrievalRequest
from app.services.source_retrieval.policy import validate_content_type,validate_url


class BasicHttpSourceProvider:
    """Small provider boundary for HTTP source retrieval.

    Production deployments should add domain allowlists, robots/terms checks,
    rate limits, caching, retries, observability, and a hardened network layer.
    """

    def retrieve(self, request: RetrievalRequest) -> RetrievedDocument:
        validate_url(request.url)

        req=urllib.request.Request(
            request.url,
            headers={"User-Agent":"AI-Content-Factory/1.0"},
        )

        with urllib.request.urlopen(
            req,
            timeout=request.timeout_seconds,
        ) as response:
            content_type=response.headers.get(
                "Content-Type","text/plain"
            )
            validate_content_type(
                content_type,
                request.allowed_content_types,
            )

            raw=response.read(request.max_bytes+1)
            if len(raw)>request.max_bytes:
                raise ValueError("Source exceeds configured maximum size")

            encoding=response.headers.get_content_charset() or "utf-8"
            text=raw.decode(encoding,errors="replace")

            if content_type.lower().startswith("text/html"):
                text=extract_text_from_html(text)

            return RetrievedDocument(
                source_id="retrieved-"+str(abs(hash(request.url))),
                url=request.url,
                title=request.url,
                text=text,
                content_type=content_type,
                status_code=getattr(response,"status",200),
            )
