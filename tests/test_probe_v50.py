from pathlib import Path

from app.services.sync.probe import FFProbeMediaProbe


def test_probe_missing_file_fails_cleanly(tmp_path):
    probe = FFProbeMediaProbe()
    if not probe.available():
        return

    missing = tmp_path / "missing.mp4"
    try:
        probe.duration_seconds(str(missing))
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("Expected FileNotFoundError")


def test_probe_reports_unavailable_binary(monkeypatch, tmp_path):
    probe = FFProbeMediaProbe(ffprobe_binary="binary-that-does-not-exist")
    assert not probe.available()
    try:
        probe.duration_seconds(str(tmp_path / "video.mp4"))
    except RuntimeError as exc:
        assert "ffprobe is required" in str(exc)
    else:
        raise AssertionError("Expected missing ffprobe failure")
