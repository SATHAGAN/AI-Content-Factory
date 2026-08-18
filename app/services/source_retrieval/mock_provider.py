from __future__ import annotations

from app.services.source_retrieval.models import RetrievedDocument,RetrievalRequest


class MockSourceProvider:
    def retrieve(self, request: RetrievalRequest) -> RetrievedDocument:
        return RetrievedDocument(
            source_id="source-mock",
            url=request.url,
            title="Mock source",
            text=(
                "This is deterministic source text used for tests. "
                "It contains enough material for downstream processing."
            ),
            publisher="Mock Publisher",
        )
