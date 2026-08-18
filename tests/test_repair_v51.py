from app.services.repair.executor import RepairExecutor
from app.services.repair.models import RepairAction, RepairRequest
from app.services.repair.planner import RepairPlanner


def test_no_repair_when_already_synchronized():
    plan=RepairPlanner().plan(RepairRequest(
        audio_duration_seconds=10,
        video_duration_seconds=10.1,
    ))
    assert plan.action == RepairAction.NONE


def test_audio_longer_prefers_tts_adjustment():
    plan=RepairPlanner().plan(RepairRequest(
        audio_duration_seconds=11,
        video_duration_seconds=10,
        current_tts_speed=1.0,
    ))
    assert plan.action == RepairAction.ADJUST_TTS_SPEED
    assert plan.target_tts_speed is not None
    assert plan.target_tts_speed > 1.0


def test_video_longer_trims_video():
    plan=RepairPlanner().plan(RepairRequest(
        audio_duration_seconds=9,
        video_duration_seconds=10,
    ))
    assert plan.action == RepairAction.TRIM_VIDEO
    assert plan.target_video_duration_seconds == 9


def test_max_attempts_go_to_manual_review():
    plan=RepairPlanner().plan(RepairRequest(
        audio_duration_seconds=11,
        video_duration_seconds=10,
        attempt=3,
    ))
    assert plan.action == RepairAction.MANUAL_REVIEW
    assert not plan.retryable


def test_executor_without_adapter_is_safe():
    plan=RepairPlanner().plan(RepairRequest(
        audio_duration_seconds=11,
        video_duration_seconds=10,
    ))
    result=RepairExecutor().execute(plan)
    assert not result.success
    assert "adapter" in result.message


def test_executor_delegates_tts_adjustment():
    plan=RepairPlanner().plan(RepairRequest(
        audio_duration_seconds=11,
        video_duration_seconds=10,
    ))
    result=RepairExecutor(tts_adapter=object()).execute(plan)
    assert result.success
    assert result.metadata["target_speed"] > 1.0


def test_executor_delegates_video_trim():
    plan=RepairPlanner().plan(RepairRequest(
        audio_duration_seconds=9,
        video_duration_seconds=10,
    ))
    result=RepairExecutor(video_adapter=object()).execute(plan)
    assert result.success
    assert result.metadata["target_duration"] == 9
