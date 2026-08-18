from app.services.recovery.prompt_rewriter import RegenerationPromptRewriter


def test_rewriter_adds_reason_specific_constraints():
    prompt=RegenerationPromptRewriter().rewrite(
        {"visual_prompt":"A child reads a book."},
        ["character_consistency","narration_alignment"],
        [{"message":"Character clothing changed."}],
    )
    assert "character" in prompt.lower()
    assert "narration" in prompt.lower()
    assert "clothing" in prompt.lower()
