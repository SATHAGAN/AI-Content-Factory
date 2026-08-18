from __future__ import annotations

from app.services.research.models import (
    ResearchClaim,
    ResearchPacket,
    SourceReference,
)


class MockResearchProvider:
    """Deterministic research provider for tests.

    It intentionally does not access the internet.
    """

    def research(self, topic: str, *, category: str) -> ResearchPacket:
        source=SourceReference(
            source_id="source-001",
            title="Example reference",
            url="https://example.com/reference",
            publisher="Example Publisher",
        )
        claim=ResearchClaim(
            claim_id="claim-001",
            text=f"Verified research placeholder for: {topic}",
            source_ids=(source.source_id,),
            confidence=0.95,
            importance="high",
        )
        return ResearchPacket(
            topic=topic,
            summary=f"Research summary placeholder for {topic}.",
            claims=(claim,),
            sources=(source,),
            research_required=True,
        )
