from app.services.research.mock_provider import MockResearchProvider
from app.services.research.service import ResearchService
from app.services.research.policy import research_required
from app.services.research.validator import validate_research_packet


def test_factual_categories_require_research():
    assert research_required("facts")
    assert research_required("educational")
    assert research_required("science")


def test_creative_category_can_skip_research():
    assert not research_required("kids")
    assert not research_required("motivation")


def test_research_service_validates_packet():
    result=ResearchService(MockResearchProvider()).run(
        topic="Why do stars shine?",
        category="science",
    )
    assert result["required"] is True
    packet=result["packet"]
    assert validate_research_packet(packet)==[]
    assert packet.claims[0].source_ids


def test_research_can_be_explicitly_disabled_for_a_category():
    result=ResearchService(MockResearchProvider()).run(
        topic="A fictional story",
        category="science",
        explicit_required=False,
    )
    assert result["required"] is False
    assert result["packet"] is None


def test_research_can_be_explicitly_enabled():
    result=ResearchService(MockResearchProvider()).run(
        topic="A fictional story",
        category="kids",
        explicit_required=True,
    )
    assert result["required"] is True
