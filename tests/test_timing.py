import pytest
from app.services.sync.audio_timing import AudioTimingPlanner


def test_audio_timing_keep():
    decision = AudioTimingPlanner().decide(10, 10.2)
    assert decision.action == "keep"


def test_audio_timing_stretch():
    decision = AudioTimingPlanner().decide(10, 11)
    assert decision.action == "time_stretch"
    assert decision.speed_factor > 1


def test_audio_timing_regenerate_if_delta_too_large():
    decision = AudioTimingPlanner().decide(10, 20)
    assert decision.action == "regenerate_or_recut"


def test_invalid_duration():
    with pytest.raises(ValueError):
        AudioTimingPlanner().decide(0, 2)
