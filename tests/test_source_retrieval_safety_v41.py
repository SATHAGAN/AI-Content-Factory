import pytest

from app.services.source_retrieval.safety import reject_obvious_private_host


def test_localhost_rejected():
    with pytest.raises(ValueError):
        reject_obvious_private_host("http://localhost:8080/admin")


def test_public_host_not_rejected_by_obvious_check():
    reject_obvious_private_host("https://example.com")
