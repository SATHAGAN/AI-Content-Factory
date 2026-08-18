from __future__ import annotations

from app.services.research.models import ResearchPacket


def validate_research_packet(packet: ResearchPacket) -> list[str]:
    errors=[]

    source_ids={source.source_id for source in packet.sources}

    if not packet.topic.strip():
        errors.append("Research topic is empty")

    if not packet.summary.strip():
        errors.append("Research summary is empty")

    for claim in packet.claims:
        if not claim.text.strip():
            errors.append(f"{claim.claim_id}: empty claim")
        if not claim.source_ids:
            errors.append(f"{claim.claim_id}: no supporting sources")
        missing=[sid for sid in claim.source_ids if sid not in source_ids]
        if missing:
            errors.append(
                f"{claim.claim_id}: missing sources {', '.join(missing)}"
            )
        if not 0 <= claim.confidence <= 1:
            errors.append(f"{claim.claim_id}: confidence must be 0..1")

    return errors


def unsupported_claims(packet: ResearchPacket) -> list[str]:
    return [
        claim.claim_id
        for claim in packet.claims
        if not claim.source_ids
    ]
