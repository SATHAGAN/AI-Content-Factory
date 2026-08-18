from app.services.judge.prompt import build_judge_prompt


def test_judge_prompt_contains_required_evidence_inputs():
    prompt=build_judge_prompt(
        scene={"number":1,"visual_prompt":"fox","narration":"hello"},
        frame_paths=["frame1.jpg"],
        audio_transcript="hello",
    )
    assert "frame1.jpg" in prompt
    assert "hello" in prompt
    assert "JSON only" in prompt
