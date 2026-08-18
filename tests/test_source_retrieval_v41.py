from app.services.source_retrieval.models import RetrievalRequest
from app.services.source_retrieval.mock_provider import MockSourceProvider
from app.services.source_retrieval.service import SourceRetrievalService
from app.services.source_retrieval.policy import validate_content_type,validate_url
import pytest


def test_mock_retrieval_returns_document():
    doc=SourceRetrievalService(MockSourceProvider()).retrieve(
        "https://example.com/article"
    )
    assert doc.text
    assert doc.url=="https://example.com/article"


def test_only_http_https_allowed():
    with pytest.raises(ValueError):
        validate_url("file:///etc/passwd")


def test_missing_host_rejected():
    with pytest.raises(ValueError):
        validate_url("https:///bad")


def test_content_type_policy():
    validate_content_type("text/html; charset=utf-8",("text/html",))
    with pytest.raises(ValueError):
        validate_content_type("image/png",("text/html",))


def test_request_defaults():
    request=RetrievalRequest(url="https://example.com")
    assert request.timeout_seconds==15.0
    assert request.max_bytes==5_000_000
