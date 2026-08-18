from app.services.orchestration.models import MediaState, RepairRunStatus
from app.services.orchestration.pipeline import MediaRepairOrchestrator


def test_already_synced_media_passes():
    state = MediaState(
        audio_duration_seconds=10,
        video_duration_seconds=10,
        audio_path="voice.wav",
        video_path="scene.mp4",
    )
    result = MediaRepairOrchestrator().run_until_terminal(state)
    assert result.status == RepairRunStatus.PASSED
    assert result.action == "continue"


def test_longer_video_is_trimmed_and_then_passes():
    state = MediaState(
        audio_duration_seconds=9,
        video_duration_seconds=10,
        audio_path="voice.wav",
        video_path="scene.mp4",
    )
    result = MediaRepairOrchestrator().run_until_terminal(state)
    assert result.status == RepairRunStatus.PASSED
    assert result.state.video_duration_seconds == 9
    assert any(e["event"] == "repair_applied" for e in result.history)


def test_longer_audio_is_retimed_and_then_passes():
    state = MediaState(
        audio_duration_seconds=11,
        video_duration_seconds=10,
        tts_speed=1.0,
        audio_path="voice.wav",
        video_path="scene.mp4",
    )
    result = MediaRepairOrchestrator().run_until_terminal(state)
    assert result.status == RepairRunStatus.PASSED
    assert result.state.audio_duration_seconds <= 10.35


def test_missing_media_goes_to_manual_review():
    state = MediaState(
        audio_duration_seconds=0,
        video_duration_seconds=10,
        audio_path=None,
        video_path="scene.mp4",
    )
    result = MediaRepairOrchestrator().run_until_terminal(state)
    assert result.status == RepairRunStatus.MANUAL_REVIEW


def test_history_is_preserved():
    state = MediaState(
        audio_duration_seconds=9,
        video_duration_seconds=10,
        audio_path="voice.wav",
        video_path="scene.mp4",
    )
    result = MediaRepairOrchestrator().run_until_terminal(state)
    assert len(result.history) >= 2
    assert result.history[0]["event"] == "repair_applied"
    assert result.history[-1]["event"] == "sync_pass"
