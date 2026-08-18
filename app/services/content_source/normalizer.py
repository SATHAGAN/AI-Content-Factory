from __future__ import annotations

import re

from app.services.content_source.models import ContentRequest,ContentSource,SourceType


class ContentNormalizer:
    def normalize(self, request: ContentRequest) -> ContentSource:
        content=request.content.strip()

        if request.source_type == SourceType.TOPIC:
            if not content:
                raise ValueError("Topic cannot be empty")
            normalized=f"Create original content about: {content}"

        elif request.source_type == SourceType.TRANSCRIPT:
            if len(content) < 20:
                raise ValueError("Transcript is too short")
            normalized=content

        elif request.source_type == SourceType.URL:
            if not re.match(r"^https?://",content):
                raise ValueError("URL source must start with http:// or https://")
            # Fetching is intentionally delegated to a future source connector.
            normalized=content

        elif request.source_type == SourceType.FILE:
            if not content:
                raise ValueError("File source reference cannot be empty")
            normalized=content

        elif request.source_type == SourceType.GENERATED:
            normalized=content or "Generate an original creative story."

        else:
            raise ValueError(f"Unsupported source type: {request.source_type}")

        return ContentSource(
            source_id="source-"+request.source_type.value,
            source_type=request.source_type,
            content=normalized,
            title=request.title.strip(),
            language=request.language,
            category=request.category,
            metadata={
                **request.metadata,
                "target_duration_seconds":request.target_duration_seconds,
                "audience":request.audience,
                "tone":request.tone,
            },
        )
