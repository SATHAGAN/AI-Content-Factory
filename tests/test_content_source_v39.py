import pytest

from app.services.content_source.models import ContentRequest,SourceType
from app.services.content_source.pipeline import ContentSourcePipeline
from app.services.content_source.mock_llm import MockTopicLLM


def pipeline():
    return ContentSourcePipeline(MockTopicLLM())


def test_topic_source_is_normalized():
    source=pipeline().resolve(ContentRequest(
        source_type=SourceType.TOPIC,
        content="Why do stars shine?",
        category="educational",
    ))
    assert source.source_type==SourceType.TOPIC
    assert "Why do stars shine?" in source.content


def test_transcript_requires_minimum_content():
    with pytest.raises(ValueError):
        pipeline().resolve(ContentRequest(
            source_type=SourceType.TRANSCRIPT,
            content="too short",
        ))


def test_url_is_validated_but_not_fetched():
    source=pipeline().resolve(ContentRequest(
        source_type=SourceType.URL,
        content="https://example.com/article",
    ))
    assert source.source_type==SourceType.URL


def test_generated_topic_is_dynamic():
    source=pipeline().resolve(ContentRequest(
        source_type=SourceType.GENERATED,
        category="kids",
        audience="children",
    ))
    assert source.content
    assert source.source_type==SourceType.GENERATED


def test_invalid_url_is_rejected():
    with pytest.raises(ValueError):
        pipeline().resolve(ContentRequest(
            source_type=SourceType.URL,
            content="example.com",
        ))
