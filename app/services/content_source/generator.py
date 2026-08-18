from __future__ import annotations

from app.services.content_source.models import ContentRequest,ContentSource,SourceType


class TopicGenerator:
    """Provider-neutral topic generator.

    A real LLM can replace this implementation without changing the source
    pipeline.
    """

    def __init__(self,llm):
        self.llm=llm

    def generate(self, request: ContentRequest) -> ContentSource:
        if request.source_type != SourceType.GENERATED:
            raise ValueError("TopicGenerator requires GENERATED source type")

        topic=self.llm.generate(
            system=(
                "Generate one original, audience-appropriate content idea. "
                "Return plain text only."
            ),
            prompt=(
                f"Category: {request.category}\n"
                f"Audience: {request.audience}\n"
                f"Tone: {request.tone}\n"
                f"Language: {request.language}\n"
                "Return one concise topic."
            ),
            response_format="text",
        ).strip()

        if not topic:
            raise ValueError("LLM returned an empty topic")

        return ContentSource(
            source_id="generated-topic",
            source_type=SourceType.GENERATED,
            content=topic,
            title=topic[:100],
            language=request.language,
            category=request.category,
            metadata=dict(request.metadata),
        )
