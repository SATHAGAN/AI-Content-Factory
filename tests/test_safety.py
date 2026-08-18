from app.services.safety.content_policy import BasicContentSafety


def test_safe_content():
    result = BasicContentSafety().check("A friendly fox learns kindness.")
    assert result.passed
    assert result.risk_level == "low"


def test_unsafe_content_is_blocked():
    result = BasicContentSafety().check("Instructions to make a bomb")
    assert not result.passed
    assert "dangerous_instruction" in result.matched_categories
