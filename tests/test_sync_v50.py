from app.services.sync.analyzer import AVSyncAnalyzer
from app.services.sync.gate import SyncQualityGate
from app.services.sync.models import SyncConfig, SyncStatus


def test_exact_sync_passes():
    report = AVSyncAnalyzer().analyze(
        audio_duration_seconds=10.0,
        video_duration_seconds=10.0,
    )
    assert report.status == SyncStatus.PASS
    assert report.score == 1.0
    assert report.passed


def test_small_mismatch_passes():
    report = AVSyncAnalyzer().analyze(
        audio_duration_seconds=10.0,
        video_duration_seconds=10.10,
    )
    assert report.status == SyncStatus.PASS
    assert report.duration_delta_seconds == 0.1


def test_warning_zone_is_not_silently_approved():
    report = AVSyncAnalyzer().analyze(
        audio_duration_seconds=10.0,
        video_duration_seconds=10.25,
    )
    assert report.status == SyncStatus.WARNING
    assert "duration_mismatch_warning" in report.reasons


def test_large_mismatch_fails():
    report = AVSyncAnalyzer().analyze(
        audio_duration_seconds=10.0,
        video_duration_seconds=10.50,
    )
    assert report.status == SyncStatus.FAIL
    assert "duration_mismatch" in report.reasons
    assert report.score == 0.0


def test_missing_audio_fails():
    report = AVSyncAnalyzer().analyze(
        audio_duration_seconds=0.0,
        video_duration_seconds=10.0,
        audio_present=False,
    )
    assert report.status == SyncStatus.FAIL
    assert "audio_missing" in report.reasons


def test_custom_thresholds():
    analyzer = AVSyncAnalyzer(SyncConfig(
        max_duration_delta_seconds=1.0,
        warning_duration_delta_seconds=0.5,
    ))
    report = analyzer.analyze(
        audio_duration_seconds=10,
        video_duration_seconds=10.4,
    )
    assert report.status == SyncStatus.PASS


def test_quality_gate_actions():
    gate = SyncQualityGate()

    passed = AVSyncAnalyzer().analyze(
        audio_duration_seconds=10,
        video_duration_seconds=10,
    )
    decision = gate.decide(passed)
    assert decision.approved
    assert decision.action == "continue"

    failed = AVSyncAnalyzer().analyze(
        audio_duration_seconds=10,
        video_duration_seconds=11,
    )
    decision = gate.decide(failed)
    assert not decision.approved
    assert decision.retryable
    assert decision.action == "regenerate_or_adjust"
