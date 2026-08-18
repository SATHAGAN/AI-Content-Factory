from __future__ import annotations

from app.services.research.policy import research_required
from app.services.research.validator import validate_research_packet


class ResearchService:
    def __init__(self, provider):
        self.provider=provider

    def run(
        self,
        *,
        topic: str,
        category: str,
        explicit_required: bool | None = None,
    ):
        required=research_required(
            category,
            explicit=explicit_required,
        )

        if not required:
            return {
                "required":False,
                "packet":None,
            }

        packet=self.provider.research(topic,category=category)
        errors=validate_research_packet(packet)
        if errors:
            raise ValueError("; ".join(errors))

        return {
            "required":True,
            "packet":packet,
        }
