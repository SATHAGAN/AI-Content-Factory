from app.services.research.models import (
    ResearchClaim,
    ResearchPacket,
    SourceReference,
)
from app.services.research.validator import validate_research_packet


def test_claim_without_source_is_rejected():
    packet=ResearchPacket(
        topic="test",
        summary="summary",
        claims=(
            ResearchClaim(
                claim_id="c1",
                text="unsupported claim",
                source_ids=(),
                confidence=0.5,
            ),
        ),
        sources=(),
    )
    errors=validate_research_packet(packet)
    assert any("no supporting sources" in error for error in errors)


def test_missing_source_id_is_rejected():
    packet=ResearchPacket(
        topic="test",
        summary="summary",
        claims=(
            ResearchClaim(
                claim_id="c1",
                text="claim",
                source_ids=("missing",),
                confidence=0.5,
            ),
        ),
        sources=(
            SourceReference("source-1","A source"),
        ),
    )
    errors=validate_research_packet(packet)
    assert any("missing sources" in error for error in errors)
