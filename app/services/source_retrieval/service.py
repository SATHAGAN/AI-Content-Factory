from __future__ import annotations

from app.services.source_retrieval.models import RetrievalRequest


class SourceRetrievalService:
    def __init__(self, provider):
        self.provider=provider

    def retrieve(self,url: str):
        return self.provider.retrieve(
            RetrievalRequest(url=url)
        )
