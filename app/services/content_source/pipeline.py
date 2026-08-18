from __future__ import annotations

from app.services.content_source.generator import TopicGenerator
from app.services.content_source.models import ContentRequest,ContentSource,SourceType
from app.services.content_source.normalizer import ContentNormalizer


class ContentSourcePipeline:
    def __init__(self,llm):
        self.normalizer=ContentNormalizer()
        self.generator=TopicGenerator(llm)

    def resolve(self, request: ContentRequest) -> ContentSource:
        if request.source_type == SourceType.GENERATED:
            return self.generator.generate(request)
        return self.normalizer.normalize(request)
